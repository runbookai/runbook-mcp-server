1. Run the following command:

```
export KUBECONFIG={env[kubernetes][clusters][prod][kubeconfigPath]}
kubectl config use-context {env[kubernetes][clusters][prod][kubeconfigContext]}

kubectl get deployments {var.name} -n {env[kubernetes][deployments][{var.name}][namespace]} -o yaml | grep image
```

This tells the latest version deployed in the production. The image tag is "latest prod deploy".

2. Run the following command:

```
cd {env[github][repoBaseDir]}/{env[kubernetes][deployments][{var.name}][githubRepo]}
git checkout main
git pull
git log log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit | head -100
```

This tells the recent commit to the my-app.

3. Show the above output to me and ask if we want to proceed or not.

4. Send the output of the above command to the Slack channel {env[slack][deployAnnouncement]}.

Instead of the entire output, we would like to show commit logs till it has the same tag as "latest prod deploy".
(Do not include the commit that has the same as "latest staging deploy".)
