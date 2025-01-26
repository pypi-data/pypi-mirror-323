# blemli_mail
quickly send a mail to problemli (or someone else)

## usage
easy:
```python
import blemli_mail
blemli_mail.send("message")
```

or fancy:
```python
import blemli_mail
blemli_mail.send("message",subject="Testmail", level="INFO",recipient="xyz@abc.com")
```

you have to add this to your .env:
```python
BM_SERVER="server.example.com"
BM_USER="user@server.example.com"
BM_PASSWORD="******************"
BM_SERVICE="servicename"
BM_RECIPIENT="mail@example.com"
```