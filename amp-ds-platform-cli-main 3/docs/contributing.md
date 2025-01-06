# Contributing

## An Overview of Contributing to the Platform CLI

Prior to contributing, please ensure you have git authorship correctly configured

    git config --global user.name [username]
    git config --global user.email [email]

### Creating a Branch

Once git is configured, you’ll need to create a new branch for the feature (or bug fix)

    git checkout -b [branch name]

The above command will create and checkout your branch. The branch should conform to the following naming convention

    {feature,bug}/[ticket number]

**An optional build keyword can be added to create a development release. A development release should be used for localized testing, if needed.**

### Adding a feature or bug fix

Once the branch is created, you can start making changes locally! Features should include tests (when applicable) and conform to all PEP-8 standards. We have implemented automatic checks via SonarQube to ensure styles remain consistent between each pull request.

As you are adding a feature/bug fix, be sure commit your code

    [IF APPLICABLE] git add [file or .]
    git commit -m "[short, descriptive message]"

As you are making code changes, consider rebasing your branch as you develop. It will ensure that you are pulling the latest changes from the main branch and prevent large merge conflicts. Assuming you have your branch checked out and you want to remain up to date with the latest development branch,

    git checkout develop && git pull origin develop
    git checkout [branch name] && git rebase develop 

This should rebase your branch onto the development branch. Be sure to fix any merge conflicts that may arise after the rebase. Once your commits are ready to be reviewed, you can push the changes to the remote repository. Please squash commits prior to pushing for a code review. The following will squash the last N commits and push to the remote origin:

    git reset --soft HEAD~[N] && git commit -m "[descriptive commit message]"
    git push origin [branch name]

Once pushed, be sure to visit the GitHub repository and create a pull request. Each pull request should have the following:

1. Short title explaining the change
2. A description giving additional context. If the Zenhub ticket contains more context, please include a link.
3. Proof of functionality - this can be a screen shot of command line tests, a video proving it was tested, or a link to automated tests. Please consider all edge cases as you test locally.

Once the pull request is filled out, you can click the create button.

### Get it reviewed

After the pull request is created, it will begin to perform the automated checks via SonarQube. If any checks fail, be sure to make any fixes. After the pull request passes the automated checks, request a code review. ADL requires an approval from one of the core developers prior to merge. A core developer will review the code for style consistency, functionality, and tests. Code reviews are an opportunity for developers to ensure the library remains manageable and an opportunity to learn from one another so this is a critical part in the workflow.

### Merge

Once the code is approved by a core developer, it is ready to merge. Depending on how long the code review takes, you may need to rebase and fix any merge conflicts. This is why consistent rebasing is important as you develop a feature/bug fix. Once ready, merge the pull request into the develop  branch.

### Clean up

Congratulations! Your feature/bug fix is now in the development phase and it will be released in the next release cycle! Once merged, you can now delete your development branch. You can do this via the UI after you click the merge button. Please delete your develop branch as it helps us keep the repository easier to use. 

Thank you for contributing! 