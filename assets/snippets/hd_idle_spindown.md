**Observe current HDD status (active / standby)**
`sudo hdparm -C /dev/sda`

List all disks:
`lsblk`

Get disk UUID:
`blkid /dev/sda`

**Spindown time** (not sure if it's for hdparm or hd-idle)
- **0** : désactive ; le périphérique ne rentrera pas en mode _stand-by_.
- de **1** à **240** : spécifie des multiples de 5 secondes, avec des temps morts de 5 secondes à 20 minutes.   
- De **241** à **251** : spécifie de 1 à 11 unités de temps de 30 minutes chacune, avec des temps morts de 30 minutes à 5 h 30.    
- **252** : spécifie un temps mort de 21 minutes.    
- **253** : est une période de temps mort définie par le fabriquant, entre 8 à 12 heures.    
- **254** : réservée !    
- **255** : est interprétée comme 21 minutes plus 15 secondes.
