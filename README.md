# nofluffscrapper

This selenium script visits `https://nofluffjobs.com/` and based on specified criteria looks for job offers that suit mentioned skills.

Use flask GUI to specify your configuration and add skills to your stack.
If there is a tech that is no-go, you can exclude it with leading `-` sing, eg. (`-ios`).

---

By default script sends report to email. You should pass `EMAIL` and `PASSWORD` as enviromental variables, or you can use `--no_email` flag which will save the report to `.txt` file. (eg. `python3 scrapper.py --no_email`)
