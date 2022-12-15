if [ -f ~/.bashrc ]; then
    grep -q "BROADLINK" /etc/sudoers
    if [ $? -ne 0 ]; then
        cat << 'EOF' >> /etc/sudoers
Defaults             env_keep+=BROADLINK
EOF
    fi
fi

echo "export BROADLINK=/home/pi/broadlink" | sudo tee -a /etc/profile.d/broadlink.sh

