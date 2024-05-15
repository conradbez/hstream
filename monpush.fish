#!/usr/bin/env fish

# Function to monitor GitHub Actions run after push
function monitor-run
    # Wait for a few seconds to ensure the GitHub Actions workflow starts
    sleep 5

    # Get the latest run ID
    set LATEST_RUN_ID (gh run list --limit 1 --json databaseId -q '.[0].databaseId')
    open "https://github.com/conradbez/hstream/actions/runs/$LATEST_RUN_ID"
    # Watch the latest run logs
    gh run watch $LATEST_RUN_ID

    # Get the status of the latest run
    set RUN_STATUS (gh run view $LATEST_RUN_ID --json conclusion -q '.conclusion')

    # Print the status
    echo "The latest run concluded with status: $RUN_STATUS"
    echo "https://github.com/conradbez/hstream/actions/runs/$LATEST_RUN_ID"
end

git push

# Call the function to monitor the run
monitor-run
