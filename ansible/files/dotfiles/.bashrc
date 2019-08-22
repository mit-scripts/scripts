# .bashrc

# User specific aliases and functions

alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'

DEFAULTVISUAL=emacs
if [ "$SSH_GSSAPI_NAME" = "adehnert/root@ATHENA.MIT.EDU" ]; then
        DEFAULTVISUAL=vim
fi
export VISUAL=${VISUAL:-$DEFAULTVISUAL}

# Source global definitions
if [ -f /etc/bashrc ]; then
        . /etc/bashrc
fi

alias vi=vim
alias view='vim -R'

logger -p authpriv.warning -t bash -- "Root bash shell for ${SSH_GSSAPI_NAME:-unknown} from ${SSH_CLIENT:-local}"
