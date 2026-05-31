# Issue Explorer

The Issue Explorer is responsible for fetching and formatting issues for repositories. It provides:

- Listing with pagination support.
- Issue detail view (concise or `--full` with timestamps and full body).
- Simple search and label filters.

It relies on the GitHub Client to page through the repository's issues endpoint.
