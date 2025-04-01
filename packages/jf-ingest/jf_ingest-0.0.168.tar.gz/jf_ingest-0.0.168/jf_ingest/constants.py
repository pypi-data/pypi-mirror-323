class Constants:
    JELLYFISH_USER_AGENT = f'jellyfish/1.0'
    # This is how many bytes are in a MB. This is used when
    # determining how much data to upload to S3 (we generally)
    # batch files by ~50 MBs
    MB_SIZE_IN_BYTES = 1048576
    JIRA_ISSUES_UNCOMPRESSED_FILE_SIZE = 50 * MB_SIZE_IN_BYTES
    # 250 is the default largest value we can pull from Jira Server
    # For cloud it's 100, but we have logic to check what Jira
    # limits us to and reduce our batch size to that
    MAX_ISSUE_API_BATCH_SIZE = 250
    # use the 10k issues pull new sync method
    NEW_SYNC_FF_NAME = 'makara-jf-ingest-use-new-sync-2024Q4'
    # Uses a pull-by-id approach to fetching sprints
    PULL_SPRINTS_BY_ID = 'makara-pull-sprints-by-id-2024Q4'
    MAKARA_JIRA_PROJECT_JQL_BATCH_SIZE = 'makara-jira-project-jql-batch-size-2025Q1'
