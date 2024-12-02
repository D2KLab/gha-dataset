# Supported Commands

1. adduser

Categories: USER_MANAGEMENT

    adduser [login]

2. apk

Categories: PACKAGE_MANAGEMENT

    apk add [packages...] Categories: INSTALL_PACKAGES
    apk del [packages...] Categories: UNINSTALL_PACKAGES
    apk fix
    apk update Categories: UPDATE_PACKAGES
    apk info
    apk search
    apk upgrade [packages...] Categories: UPGRADE_PACKAGES
    apk cache
    apk version
    apk index
    apk fetch
    apk audit
    apk verify
    apk dot
    apk policy <package>
    apk stats
    apk manifest

3. apt-add-repository

Categories: PACKAGE_MANAGEMENT

    apt-add-repository <repository>

4. apt-get

Categories: PACKAGE_MANAGEMENT

    apt-get install [packages...] Categories: INSTALL_PACKAGES
    apt-get purge [packages...]
    apt-get remove [packages...] Categories: UNINSTALL_PACKAGES
    apt-get source <package>
    apt-get build-dep [packages...]
    apt-get clean
    apt-get autoclean
    apt-get autoremove [packages...]
    apt-get check
    apt-get update Categories: UPDATE_PACKAGES
    apt-get upgrade [packages...] Categories: UPGRADE_PACKAGES
    apt-get dist-upgrade Categories: UPGRADE_PACKAGES

5. apt-key

Categories: PACKAGE_MANAGEMENT

    apt-key add <filename>
    apt-key del <keyid>
    apt-key export <keyid>
    apt-key exportall
    apt-key list
    apt-key finger
    apt-key fingerprint <key>
    apt-key adv
    apt-key update
    apt-key net-update

6. apt

Categories: PACKAGE_MANAGEMENT

    apt install [packages...] Categories: INSTALL_PACKAGES
    apt remove [packages...] Categories: UNINSTALL_PACKAGES
    apt clean
    apt autoclean
    apt autoremove [packages...]
    apt update Categories: UPDATE_PACKAGES
    apt upgrade [packages...] Categories: UPDATE_PACKAGES
    apt clean

7. basename

Categories: FILE_SYSTEM,UTILS

    basename

8. bash

Categories: SHELL

    bash

9. bundle

Categories: PACKAGE_MANAGEMENT

    bundle install Categories: INSTALL_PACKAGES
    bundle update Categories: UPDATE_PACKAGES
    bundle cache
    bundle exec
    bundle config
    bundle help
    bundle add <name> Categories: INSTALL_PACKAGES
    bundle remove <name> Categories: UNINSTALL_PACKAGES
    bundle exec

10. cat

Categories: PRINT

    cat [PATH...]

11. cd

Categories: NAVIGATION,FILE_SYSTEM

    cd <path>

12. chmod

Categories: FILE_PERMISSIONS

    chmod <mode> [paths...]
    chmod [paths...]

13. chown

Categories: FILE_PERMISSIONS

    chown [paths...]
    chown <owner> [paths...]

14. cmake

Categories: BUILD_SYSTEM

    cmake [options...] Categories: BUILD_PACKAGES
    cmake
    cmake Categories: INSTALL_PACKAGES
    cmake
    cmake [pathToSourceOrBuild]

15. codecov

Categories: CODE_COVERAGE

    codecov [args...]

16. composer

Categories: PACKAGE_MANAGEMENT

    composer [args...]

17. conda

Categories: PACKAGE_MANAGEMENT

    conda install [packages...] Categories: INSTALL_PACKAGES
    conda remove [packages...] Categories: UNINSTALL_PACKAGES
    conda update [packages...] Categories: UPDATE_PACKAGES
    conda create
    conda activate <environement>
    conda deactivate
    conda search <term>
    conda list
    conda info

18. ./configure

Categories: BUILD_SYSTEM

    ./configure [ignores...]

19. coverage

Categories: CODE_COVERAGE

    coverage [args...]

20. coveralls

Categories: CODE_COVERAGE

    coveralls [args...]

21. cp

Categories: FILE_SYSTEM

    cp [paths...]

22. ctest

Categories: TEST_PACKAGES

    ctest [args...]

23. curl

Categories: DOWNLOAD

    curl [url]

24. diff

Categories: DIFF

    diff [args...]

25. dnf

Categories: PACKAGE_MANAGEMENT

    dnf install [packages...] Categories: INSTALL_PACKAGES
    dnf debuginfo-install [packages...] Categories: INSTALL_PACKAGES
    dnf clean all
    dnf update Categories: UPDATE_PACKAGES
    dnf upgrade Categories: UPGRADE_PACKAGES
    dnf check-update
    dnf autoremove
    dnf builddep [packages...] Categories: BUILD_PACKAGES

26. docker-php-ext-install

Categories: PACKAGE_MANAGEMENT

    docker-php-ext-install [packages...] Categories: INSTALL_PACKAGES

27. docker

Categories: VIRTUALIZATION

    docker run
    docker exec
    docker ps
    docker build
    docker pull
    docker push
    docker images
    docker login
    docker login azure
    docker logout
    docker logout azure
    docker search
    docker version
    docker info

28. dotnet

Categories: BUILD_SYSTEM

    dotnet build [options...] Categories: BUILD_PACKAGES
    dotnet build-server [options...] Categories: BUILD_PACKAGES
    dotnet clean [options...]
    dotnet exec [options...]
    dotnet help [options...]
    dotnet migrate [options...]
    dotnet msbuild [options...]
    dotnet new [options...]
    dotnet pack [options...]
    dotnet publish [options...]
    dotnet restore [options...]
    dotnet run [options...]
    dotnet sdk check [options...]
    dotnet sln [options...]
    dotnet store [options...]
    dotnet test [options...] Categories: TEST_PACKAGES

29. dpkg-architecture

Categories: PACKAGE_MANAGEMENT

    dpkg-architecture

30. dpkg

Categories: PACKAGE_MANAGEMENT

    dpkg <dir>
    dpkg <dir>
    dpkg

31. echo

Categories: PRINT

    echo [items...]

32. exit

Categories: CONTROL_FLOW

    exit <code>

33. export

Categories: ENVIRONMENT

    export <target>

34. false

Categories: UTILS

    false

35. find

Categories: FILE_SYSTEM,SEARCH

    find <target>

36. firefox

Categories: BROWSER

    firefox <url>

37. gem

Categories: PACKAGE_MANAGEMENT

    gem install [gems...] Categories: INSTALL_PACKAGES
    gem update [gems...] Categories: UPGRADE_PACKAGES
    gem cleanup
    gem list
    gem build <path> Categories: BUILD_PACKAGES

38. gh

Categories:

    gh auth
    gh auth login
    gh auth logout
    gh auth refresh
    gh auth setup-git
    gh auth status
    gh auth token
    gh browse
    gh codespace
    gh codespace code
    gh codespace cp
    gh codespace create
    gh codespace delete
    gh codespace edit
    gh codespace jupyter
    gh codespace list
    gh codespace logs
    gh codespace ports
    gh codespace ports forward
    gh codespace ports visibility
    gh codespace rebuild
    gh codespace ssh
    gh codespace stop
    gh codespace view
    gh gist
    gh gist clone
    gh gist create
    gh gist delete
    gh gist edit
    gh gist list
    gh gist rename
    gh gist view
    gh issue
    gh issue create
    gh issue list
    gh issue status
    gh org
    gh org list
    gh pr
    gh pr create
    gh pr list
    gh pr status
    gh project
    gh project close
    gh project copy
    gh project create
    gh project delete
    gh project edit
    gh project field-create
    gh project field-delete
    gh project field-list
    gh project item-add
    gh project item-archive
    gh project item-create
    gh project item-delete
    gh project item-edit
    gh project item-list
    gh project list
    gh project mark-template
    gh project view
    gh release
    gh release create
    gh release list
    gh repo
    gh repo create
    gh repo list

39. git

Categories: VERSION_CONTROL

    git submodule init
    git submodule update
    git pull Categories: VERSION_CONTROL_PULL
    git remote set-url <target> <url>
    git reset <target>
    git rev-parse <target>
    git clone <url> [directory] Categories: VERSION_CONTROL_CLONE
    git init
    git checkout <target>
    git gc
    git config <setting> <value>
    git fetch [args...]
    git describe
    git commit
    git diff [...args] Categories: DIFF
    git cat-file <file> Categories: PRINT
    git clean
    git

40. go

Categories: BUILD_SYSTEM,DEVELOPMENT

    go get [packages...] Categories: INSTALL_PACKAGES
    go vet
    go fmt
    go version
    go install [packages...] Categories: INSTALL_PACKAGES
    go test [packages...] Categories: TEST_PACKAGES
    go clean
    go build [packages...] Categories: BUILD_PACKAGES
    go mod [arg]
    go env [arg] Categories: ENVIRONMENT
    go generate [path]
    go list [path]

41. google-chrome

Categories: BROWSER

    google-chrome <URL>

42. gpg

Categories: SECURITY

    gpg [targets...]

43. ./gradlew

Categories: PACKAGE_MANAGEMENT

    ./gradlew install Categories: INSTALL_PACKAGES
    ./gradlew build Categories: BUILD_PACKAGES
    ./gradlew clean
    ./gradlew test Categories: TEST_PACKAGES
    ./gradlew assemble
    ./gradlew publish Categories: PUBLISH_PACKAGES

44. grep

Categories: SEARCH,FILE_SYSTEM

    grep <pattern> [paths...]

45. groupadd

Categories: USER_MANAGEMENT

    groupadd <group>

46. jq

Categories: DATA_PROCESSING

    jq <filter> [PATH...]

47. ldconfig

Categories:

    ldconfig

48. ln

Categories: FILE_SYSTEM

    ln <target> <link>
    ln <target>
    ln [targets...]
    ln [targets...]
    ln [targets...]

49. locale-gen

Categories: LOCALIZATION

    locale-gen

50. ls

Categories: FILE_SYSTEM

    ls [PATH...]

51. make

Categories: BUILD_SYSTEM

    make [target] [args...] Categories: BUILD_PACKAGES

52. md5

Categories: HASH

    md5 [paths...]

53. mkdir

Categories: FILE_SYSTEM

    mkdir [paths...]

54. mktemp

Categories: FILE_SYSTEM

    mktemp [template]

55. mv

Categories: FILE_SYSTEM

    mv [paths...]

56. mvn

Categories: PACKAGE_MANAGEMENT

    mvn install Categories: INSTALL_PACKAGES
    mvn clean
    mvn compile Categories: BUILD_PACKAGES
    mvn test Categories: TEST_PACKAGES
    mvn package Categories: BUILD_PACKAGES
    mvn deploy Categories: DEPLOY_PACKAGES

57. node

Categories: DEVELOPMENT

    node [args...]

58. npm

Categories: PACKAGE_MANAGEMENT

    npm install [packages...] Categories: INSTALL_PACKAGES
    npm i [packages...] Categories: INSTALL_PACKAGES
    npm add [packages...] Categories: INSTALL_PACKAGES
    npm ci Categories: INSTALL_PACKAGES
    npm uninstall [packages...] Categories: UNINSTALL_PACKAGES
    npm remove [packages...] Categories: UNINSTALL_PACKAGES
    npm build [folder] Categories: BUILD_PACKAGES
    npm TEST [args...] Categories: TEST_PACKAGES
    npm run build [args...] Categories: BUILD_PACKAGES
    npm run [args...] Categories: RUN_PACKAGES
    npm run-script [args...] Categories: RUN_PACKAGES
    npm cache clean
    npm cache rm
    npm cache clear
    npm config set <key> <value>
    npm config set <combined>
    npm link
    npm prune [packages...] Categories: UNINSTALL_PACKAGES
    npm

59. nproc

Categories: SYSTEM_INFO

    nproc

60. pecl

Categories: PACKAGE_MANAGEMENT

    pecl -v [options...]
    pecl -q [options...]
    pecl -c  [options...]
    pecl -C  [options...]
    pecl -d  [options...]
    pecl -D  [options...]
    pecl -G [options...]
    pecl -S [options...]
    pecl -s [options...]
    pecl -y  [options...]
    pecl -V [options...]
    pecl build [options...] Categories: BUILD_PACKAGES
    pecl bundle [options...]
    pecl channel-alias [options...]
    pecl channel-delete [options...]
    pecl channel-discover [options...]
    pecl channel-info [options...]
    pecl channel-login [options...]
    pecl channel-logout [options...]
    pecl channel-update [options...]
    pecl clear-cache [options...]
    pecl config-create [options...]
    pecl config-get [options...]
    pecl config-help [options...]
    pecl config-set [options...]
    pecl config-show [options...]
    pecl convert [options...]
    pecl cvsdiff [options...] Categories: DIFF
    pecl cvstag [options...]
    pecl download [options...]
    pecl download-all [options...]
    pecl info [options...]
    pecl install [options...]
    pecl list [options...]
    pecl list-all [options...]
    pecl list-channels [options...]
    pecl list-files [options...]
    pecl list-upgrades [options...]
    pecl login [options...]
    pecl logout [options...]
    pecl make-rpm-spec [options...]
    pecl makerpm [options...]
    pecl package [options...]
    pecl package-dependencies [options...]
    pecl package-validate [options...]
    pecl pickle [options...]
    pecl remote-info [options...]
    pecl remote-list [options...]
    pecl run-scripts [options...]
    pecl run-tests [options...] Categories: TEST_PACKAGES
    pecl search [options...]
    pecl shell-test [options...]
    pecl sign [options...]
    pecl svntag [options...]
    pecl uninstall [options...] Categories: UNINSTALL_PACKAGES
    pecl update-channels [options...]
    pecl upgrade [options...] Categories: UPGRADE_PACKAGES
    pecl upgrade-all [options...] Categories: UPGRADE_PACKAGES

61. php

Categories: DEVELOPMENT

    php [script] [args...]

62. pip

Categories: PACKAGE_MANAGEMENT

    pip install [targets...] Categories: INSTALL_PACKAGES
    pip uninstall [targets...] Categories: UNINSTALL_PACKAGES
    pip freeze
    pip

63. printf

Categories: PRINT

    printf <format> [ARGS...]

64. pwd

Categories: FILE_SYSTEM,UTILS

    pwd

65. pytest

Categories: TEST_PACKAGES

    pytest [args...]

66. python

Categories: DEVELOPMENT

    python [args...]
    python

67. rm

Categories: FILE_SYSTEM

    rm [paths...]

68. rpm

Categories: PACKAGE_MANAGEMENT

    rpm <package>
    rpm [options...]
    rpm [packages...] Categories: INSTALL_PACKAGES
    rpm [packages...] Categories: UPGRADE_PACKAGES
    rpm [packages...]
    rpm [packages...]

69. sed

Categories: REGEX

    sed <expression> [paths...]
    sed [paths...]
    sed [paths...]
    sed [paths...]
    sed [paths...]

70. set

Categories: ENVIRONMENT

    set [args]

71. sh

Categories: SHELL

    sh

72. sha256sum

Categories: HASH

    sha256sum [files...]

73. sha512sum

Categories: HASH

    sha512sum [files...]

74. sort

Categories:

    sort [PATH...]

75. sudo

Categories: PRIVILEGES

    sudo

76. swift

Categories:

    swift

77. tar

Categories: ARCHIVE,FILE_SYSTEM

    tar [args...]

78. tee

Categories: PRINT

    tee [PATH...]

79. touch

Categories: FILE_SYSTEM

    touch [PATH...]

80. true

Categories: UTILS

    true

81. unzip

Categories: ARCHIVE

    unzip <file> [items...]

82. useradd

Categories: USER_MANAGEMENT

    useradd [login]
    useradd [login]
    useradd [login]
    useradd [login]
    useradd [login]
    useradd [login]

83. wc

Categories: FILE_SYSTEM,UTILS

    wc [paths...]

84. wget

Categories: DOWNLOAD

    wget <url>

85. which

Categories: UTILS

    which [program...]

86. xargs

Categories: UTILS

    xargs [PATH...]

87. yarn

Categories: PACKAGE_MANAGEMENT

    yarn add [modules...] Categories: INSTALL_PACKAGES
    yarn audit Categories: AUDIT_PACKAGES
    yarn autoclean
    yarn bin <executable>
    yarn lint
    yarn cache list
    yarn cache clean [modules...]
    yarn cache dir
    yarn global add [modules...]
    yarn install Categories: INSTALL_PACKAGES
    yarn run <script> Categories: RUN_PACKAGES
    yarn <script> Categories: RUN_PACKAGES
    yarn Categories: INSTALL_PACKAGES

88. yum

Categories: PACKAGE_MANAGEMENT

    yum remove [packages...] Categories: UNINSTALL_PACKAGES
    yum erase [packages...] Categories: UNINSTALL_PACKAGES
    yum clean all
    yum update [packages...] Categories: UPDATE_PACKAGES
    yum upgrade [packages...] Categories: UPGRADE_PACKAGES
    yum install [packages...] Categories: INSTALL_PACKAGES
    yum localinstall [packages...] Categories: INSTALL_PACKAGES
    yum groupinstall [packages...] Categories: INSTALL_PACKAGES
    yum versionlock [packages...]
    yum makecache
