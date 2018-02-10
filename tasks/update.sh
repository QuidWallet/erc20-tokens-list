cd ~/quid/tasks/erc20-tokens-list
git pull origin master
python compose_tokens_list.py
git add .
git commit -m "scheduled update"
git push origin master
