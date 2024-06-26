
# Read in data of message logs

message_logs_data_path <- ""
message_logs <- read.csv(message_logs_data_path)

# Read in data of experimental groups
groups <- list.files(
  path="C:\\Users\\bened\\telproject\\data"
)

experimental_groups <- data.frame()

for (i in groups) {
  data_path = paste("C:/Users/bened/telproject/data", i, sep="/")
  data = read.csv(data_path)
  experimental_groups <- plyr::rbind.fill(experimental_groups, data)
}

experimental_groups <- experimental_groups %>% 
  dplyr::mutate(Mobile = paste0("whatsapp:+65", Mobile)) %>% 
  dplyr::select(Mobile, group_id)

# Join message logs with experimental group labels

message_logs <- message_logs %>% 
  dplyr::left_join(experimental_groups, by=c("From"="Mobile"))

# Filter for messages sent to our WhatsApp numbers

researcher_whatsapp <- paste0(c("whatsapp:+65"), c('83229780', '88289194', '93831137', '94746442', '96309938'))
wa_numbers = c('whatsapp:+6581032285', 'whatsapp:+6585529684', 'whatsapp:+6585797278', 'whatsapp:+6586244900')

message_logs_to_senders <- message_logs %>% 
  dplyr::filter(Direction=="inbound" & !(From %in% researcher_whatsapp))

# Tabulate responses

message_logs_to_senders %>%  
  dplyr::filter(nchar(Body)<=180 & From!="whatsapp:+6596309938") %>% 
  #dplyr::group_by(From) %>% 
  dplyr::count(Body) %>% 
  dplyr::arrange(desc(n)) %>% 
  dplyr::as_tibble() %>% 
  print(n=100)

# Find responses that do not use quick-reply buttons

buttons <- c("Continue", "Agree", "中文", "Call back", "同意", "More details", "更多细节")

message_logs_to_senders %>% 
  dplyr::filter(!Body %in% buttons) %>% 
  dplyr::group_by(From) %>% 
  dplyr::count(Body) %>% 
  print(n=100)

# ======================================= ##
# Classify responses from study participants
# ======================================= ##

inbound_msg <- message_logs %>% 
  dplyr::filter(Direction=="inbound" & !(From %in% researcher_whatsapp)) %>% 
  dplyr::group_by(From) %>% 
  dplyr::arrange((SentDate)) %>% 
  dplyr::mutate(new_id=dplyr::row_number()) %>% 
  dplyr::ungroup() %>% 
  tidyr::pivot_wider(
    id_cols=c("From"),
    values_from = c("Body"),
    names_from=c("new_id"),
    names_prefix = c("inbound_msg_"),
  ) %>% 
  dplyr::mutate(
    agree_or_call_back = dplyr::if_any(dplyr::contains("inbound"), function (x) {x %in% c("Agree", "Call back", "中文")}),
    agree = dplyr::if_any(dplyr::contains("inbound"), function (x) {x %in% c("Agree")}),
    call_back = dplyr::if_any(dplyr::contains("inbound"), function (x) {x %in% c("Call back", "中文")}),
    continue_only = dplyr::if_any(dplyr::contains("inbound"), function (x) {x %in% c("Continue") & !agree})
  ) 

outbound_msg <- message_logs %>% 
  dplyr::filter(Direction=="outbound-api" & !(To %in% researcher_whatsapp)) %>% 
  dplyr::group_by(To) %>% 
  dplyr::arrange((SentDate)) %>% 
  dplyr::mutate(new_id=dplyr::row_number()) %>% 
  dplyr::ungroup() %>% 
  tidyr::pivot_wider(
    id_cols=c("To"),
    values_from = c("Body"),
    names_from=c("new_id"),
    names_prefix = c("outbound_msg_")
  ) 

errors <-  message_logs %>% 
  dplyr::filter(Direction=="outbound-api" & !(To %in% researcher_whatsapp)) %>% 
  dplyr::group_by(To) %>% 
  dplyr::arrange((SentDate)) %>% 
  dplyr::mutate(new_id=dplyr::row_number()) %>% 
  dplyr::ungroup() %>% 
  tidyr::pivot_wider(
    id_cols=c("To"),
    values_from = c("ErrorCode"),
    names_from=c("new_id"),
    names_prefix = c("err_code_")
  ) 
  

inbound_and_outbound <- inbound_msg %>% 
  dplyr::full_join(
    outbound_msg, 
    by=c("From"="To")
  ) %>% 
  dplyr::left_join(
    errors,
    by=c("From"="To")
  ) %>% 
  dplyr::mutate(
    spam_or_scam = dplyr::if_any(dplyr::contains("inbound"), function (x) {
      grepl("spam|scam|Spam|Scam|stop|Stop|Pass|骗子", x)
    }),
    not_interested = dplyr::if_any(dplyr::contains("inbound"), function (x) {
      grepl("not keen|No thank you|no thank you|What is|not interested|Not interested", x)
    }),
    call_to_clarify = dplyr::if_any(dplyr::contains("inbound"), function (x) {
      grepl("travel|travelling|unable to attend|[0-9]|[\U{1F300}]|number is unavailable", x)
    }),
    call_to_clarify = dplyr::if_else(dplyr::if_any(dplyr::contains("inbound"), function (x) {x=="No"}) | call_to_clarify==TRUE, TRUE, NA),
    outcome = dplyr::case_when(
      spam_or_scam==TRUE ~ "spam or scam",
      not_interested==TRUE & !spam_or_scam ~ "not interested",
      call_to_clarify==TRUE & !spam_or_scam & !not_interested ~ "call to clarify",
      call_back==TRUE & !spam_or_scam & !not_interested ~ "call back",
      continue_only==TRUE & !spam_or_scam & !not_interested ~ "call to clarify",
      agree==TRUE & !spam_or_scam & !not_interested & !call_back ~ "agree",
      base::startsWith(From, "whatsapp:+656") ~ "not whatsapp number",
      err_code_1==63024 ~ "invalid message recipient error",
      err_code_2==63016 ~ "failed to send freeform message outside allowed time window error",
      .default="no reply")
  ) %>% 
  dplyr::rowwise() %>%
  dplyr::mutate(
    no_of_outbound_messages = sum(!is.na(dplyr::c_across(dplyr::starts_with("outbound")))),
    no_of_inbound_messages = sum(!is.na(dplyr::c_across(dplyr::starts_with("inbound"))))
  )

# Calculate summary statistics for number of outbound messages

message_logs %>% 
  dplyr::filter(Direction=="outbound-api" & !(To %in% researcher_whatsapp)) %>% 
  dplyr::group_by(To) %>% 
  dplyr::arrange((SentDate)) %>% 
  dplyr::mutate(count_of_outbound_messages=dplyr::row_number()) %>% 
  dplyr::ungroup() %>% 
  dplyr::select(count_of_outbound_messages) %>% 
  summary()

