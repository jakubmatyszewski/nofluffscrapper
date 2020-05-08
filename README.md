# nofluffscrapper

This selenium script visits `https://nofluffjobs.com/` and based on specified criteria looks for job offers that suit mentioned skills.

Before using adjust `config.json` file to your needs. All properties read arguments from lists.

#### Example
```
location: ["warszawa", "remote"]
category: ["devops"]
seniority: ["trainee", "junior"]
stack: ["docker", "bash", "python", "linux", "windows",
        "english", "git", "shell", "team player",
        "communication skills", "selenium", "proactivity",
        "problem solving", "jenkins"]
no_stack: ["java", "ruby", "typescript", "android"]
```
By default script sends report to email. You should pass `EMAIL` and `PASSWORD` as enviromental variables, or you can use `--no_email` flag which will save the report to `.txt` file. (eg. `python3 scrapper.py --no_email`)

Todo:
- [ ] Skip offers that were already scanned(?)
