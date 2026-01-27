# Odoo 17 Nightly Build (from GitHub)
FROM debian:bookworm-slim

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

ENV LANG=C.UTF-8

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        dirmngr \
        fonts-noto-cjk \
        gnupg \
        git \
        libssl-dev \
        node-less \
        npm \
        python3-magic \
        python3-num2words \
        python3-odf \
        python3-pdfminer \
        python3-pip \
        python3-phonenumbers \
        python3-pyldap \
        python3-qrcode \
        python3-renderpm \
        python3-setuptools \
        python3-slugify \
        python3-vobject \
        python3-watchdog \
        python3-xlrd \
        python3-xlwt \
        xz-utils \
        libpq-dev \
        python3-dev \
        gcc \
        libsasl2-dev \
        libldap2-dev \
        libffi-dev \
        libxml2-dev \
        libxslt1-dev \
        zlib1g-dev \
        libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Install wkhtmltopdf
RUN curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && apt-get update \
    && apt-get install -y --no-install-recommends ./wkhtmltox.deb \
    && rm -rf wkhtmltox.deb /var/lib/apt/lists/*

# Install rtlcss
RUN npm install -g rtlcss

# Install PostgreSQL client
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ bookworm-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
    && GNUPGHOME="$(mktemp -d)" \
    && export GNUPGHOME \
    && gpg --batch --keyserver keyserver.ubuntu.com --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8 \
    && gpg --batch --export --armor B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8 | gpg --batch --dearmor > /etc/apt/trusted.gpg.d/postgresql.gpg \
    && rm -rf "$GNUPGHOME" \
    && apt-get update \
    && apt-get install --no-install-recommends -y postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create odoo user
RUN useradd -ms /bin/bash -d /opt/odoo odoo

# Clone Odoo 17.0 from GitHub (latest commits)
RUN git clone --depth 1 --branch 17.0 https://github.com/odoo/odoo.git /opt/odoo

# Install Python dependencies
RUN pip3 install --break-system-packages -r /opt/odoo/requirements.txt \
    && pip3 install --break-system-packages psycopg2-binary

# Create directories and set permissions
RUN mkdir -p /var/lib/odoo /etc/odoo /mnt/extra-addons \
    && chown -R odoo:odoo /var/lib/odoo /etc/odoo /mnt/extra-addons /opt/odoo \
    && chmod +x /opt/odoo/odoo-bin

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

VOLUME ["/var/lib/odoo", "/mnt/extra-addons", "/etc/odoo"]
EXPOSE 8069 8072

ENV ODOO_RC=/etc/odoo/odoo.conf

USER odoo
ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
