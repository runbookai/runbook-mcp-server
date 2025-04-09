Do the following.

1. Run the following command

```
kubectl get deployments -n my-namespace my-app -o yaml | grep image
```

This tells the latest version deployed in the staging. The image tag is "latest prod deploy".

2. Run the following command:

```
cd ~/c/my-app
git checkout main
git log log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit | head -100
```

This tells the recent commit to the my-app.

3. Show the output to me and ask if we want to proceed or not.

4. Send the output of the above command to the Slack channel `deploy-announcement`.

Instead of the entire output, we would like to show commit logs till it has the same tag as "latest prod deploy".
(Do not include the commit that has the same as "latest staging deploy".)
