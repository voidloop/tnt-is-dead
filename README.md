###### TNT is dead, long live TNT!

You can download the dump file from here: http://tntvillage.scambioetico.org.

Once you downloaded the file, its content can be transferred to a sqlite database with these commands:

```
pipenv shell
python ./main import dump_release_tntvillage_2019-08-30.csv
``` 

You can use "search" command to search inside the releases using a search string in glob format:

```
python ./main search 'Alien*'
```

I also provide "install.sh" to create a small launcher to tnt-is-dead. 
This script is optimized for my PC but you can easily edit it.
 
You can easily start a download of a bunch of magnets with this bash one liner script: 

```
# for link in $(tnt-is-dead search -gil '*silicon*s03*(2016)*'); do transmission-remote -a "$link"; done
```  

