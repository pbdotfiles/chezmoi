Put this in /etc/wsl.conf

```
[boot]
systemd=true    (or false, I'm not sure if this is the reason the process gets killed)

[user]
default=paul

[interop]
appendWindowsPath = false
```
