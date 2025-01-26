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