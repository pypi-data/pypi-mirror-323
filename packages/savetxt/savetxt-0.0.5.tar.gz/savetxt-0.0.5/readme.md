save some text (usually URLs) with associated tags

the most common way i use it (and the intended purpose for myself)

```bash
open $(savetxt cat links | fzf | awk '{print $NF}')
```
currently by default the file is stored in your home directory.

functionality:
- put 
```bash
savetxt put <filename> <tags> <link>
```
eg:
```commandline
❯ savetxt put linksfile google,youtube https://www.youtube.com/watch\?v\=xvFZjo5PgG0
❯ savetxt put linksfile hackernews,front https://news.ycombinator.com/
# file is created in $HOME/savetxt/ 
```

- cat
```bash
savetxt cat <filename>
```
eg:
```commandline
❯ savetxt cat linksfile
                      tags                                        value
0    ['google', 'youtube']  https://www.youtube.com/watch?v=xvFZjo5PgG0
1  ['hackernews', 'front']                https://news.ycombinator.com/
```