# StreamlitTester
Using [Streamlit](https://streamlit.io/) to query [PDS](https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir) and [NRL](https://digital.nhs.uk/developer/api-catalogue/national-record-locator-fhir/v3/consumer) in NHS England's [INT environment](https://digital.nhs.uk/developer/guides-and-documentation/testing#integration-testing).

**NB: This may not work, some corporate networks may block stuff that this relies on.**

# PDS
This simply does a call to `GET` a patient given the selected NHS Number, and updates the screen with some minimal details.

# NRL
This does a call to NRL to `GET` Document References for a patient with the selected NHS Number, and displays VERY minimal details about those items.

# Data / patient details
There's a small set of Patient NHS Numbers 'hard coded' into this, these are ones that are known to exist in PDS and at least the first three have record pointers in NRL.

# Secrets
This app uses two secrets, which for local running can be defined in .streamlit/secrets.toml but for deployment are defined as [secrets in the Streamlit app](https://docs.streamlit.io/library/advanced-features/secrets-management).

**APIKEY** This is the API key from the [Developer Hub](https://digital.nhs.uk/developer).

**KEY** This is the Private Key used to sign a JWT, the associated public key must be stored in  the [Developer Hub](https://digital.nhs.uk/developer), the current implementation assumes that the Key ID (`kid`) used is an imaginative "1".

