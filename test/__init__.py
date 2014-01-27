import re

# Use for validating any uuid returned :)
uuid_re = re.compile("^[a-fA-F\d]{8}-[a-fA-F\d]{4}-[a-fA-F\d]{4}-[a-fA-F\d]{4}-[a-fA-F\d]{12}$")