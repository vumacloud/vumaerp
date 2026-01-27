# Odoo 17 Nightly Build
FROM debian:bookworm-slim

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG=C.UTF-8

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        dirmngr \
        fonts-noto-cjk \
        gnupg \
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
        wkhtmltopdf \
    && curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && apt-get install -y --no-install-recommends ./wkhtmltox.deb \
    && rm -rf wkhtmltox.deb /var/lib/apt/lists/*

# Install rtlcss for RTL support
RUN npm install -g rtlcss

# Install PostgreSQL client
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ bookworm-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
    && GNUPGHOME="$(mktemp -d)" \
    && export GNUPGHOME \
    && gpg --batch --keyserver keyserver.ubuntu.com --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8 \
    && gpg --batch --export --armor B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8 | gpg --batch --dearmor > /etc/apt/trusted.gpg.d/postgresql.gpg \
    && rm -rf "$GNUPGHOME" \
    && apt-get update  \
    && apt-get install --no-install-recommends -y postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create odoo user
RUN useradd -ms /bin/bash -d /opt/odoo odoo

# Download and install latest Odoo 17 nightly
WORKDIR /opt/odoo
RUN curl -sSL https://nightly.odoo.com/17.0/nightly/src/odoo_17.0.latest.tar.gz -o odoo.tar.gz \
    && tar -xzf odoo.tar.gz --strip-components=1 \
    && rm odoo.tar.gz

# Install Python dependencies
RUN pip3 install --break-system-packages -r /opt/odoo/requirements.txt \
    && pip3 install --break-system-packages psycopg2-binary

# Create necessary directories
RUN mkdir -p /var/lib/odoo /etc/odoo /mnt/extra-addons \
    && chown -R odoo:odoo /var/lib/odoo /etc/odoo /mnt/extra-addons /opt/odoo

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set volumes
VOLUME ["/var/lib/odoo", "/mnt/extra-addons", "/etc/odoo"]

# Expose ports
EXPOSE 8069 8072

# Set default environment variables
ENV ODOO_RC=/etc/odoo/odoo.conf

USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
