# LeetCode Exporter

Automatically export all solved LeetCode solutions from your account into a GitHub repository.

## Features

- ✅ Automated web scraping using Selenium (no LeetCode API)
- ✅ Extracts source code from all solved problems
- ✅ Generates organized folder structure
- ✅ Auto-generates README with problem index
- ✅ Git integration with automatic commit and push
- ✅ Resume support (continue from where it left off)
- ✅ Progress bar with rich output
- ✅ Comprehensive logging

## Architecture

**Layered Architecture** with the following modules:

```
crawler/       - LeetCode web scraping
exporter/      - File and README generation
git/           - Git repository management
models/        - Domain entities (dataclasses)
utils/         - Logging, config, exceptions, resume state
```

## Installation

### Prerequisites

- Python 3.12+
- Chrome/Chromium browser installed
- Git installed

### Setup

1. Clone or create this project directory

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure credentials in `config.yaml`:
   ```yaml
   leetcode:
     username: your_leetcode_username
     password: your_leetcode_password
   ```

## Usage

Run the exporter:

```bash
python main.py
```

### Configuration Options

Edit `config.yaml`:

```yaml
leetcode:
  username: your_username
  password: your_password

output_path: ./exported_solutions    # Where to save solutions
repo_path: .                         # Git repository path
log_level: INFO                      # DEBUG, INFO, WARNING, ERROR
headless: true                       # false to see browser window
```

## How It Works

1. **Login** - Authenticates with LeetCode
2. **Discover** - Finds all solved problems on the problemset page
3. **Export** - For each problem:
   - Opens the problem page
   - Navigates to Submissions tab
   - Fetches the latest accepted submission
   - Extracts source code
   - Saves to `NNNN-Problem-Title/Solution.java` or `.py`
4. **Generate README** - Creates markdown index of all solutions
5. **Commit & Push** - Stages changes, commits, and pushes to remote

## Resume Capability

If the export process is interrupted, a `.leetcode_resume` checkpoint file is created. Running the exporter again will:
- Skip already exported problems
- Continue from where it left off
- Only re-fetch failed problems

To clear the resume state and start fresh:
```bash
rm .leetcode_resume
```

## Project Structure

```
leetcode-exporter/
├── crawler/
│   ├── login.py                 # LoginService
│   ├── problemset.py            # ProblemSetCrawler
│   ├── submissions.py           # SubmissionCrawler
│   ├── detail.py                # SubmissionDetailCrawler
│   └── chrome_session.py        # ChromeSessionManager
├── exporter/
│   ├── folder.py                # ExportFolderService
│   └── readme.py                # ReadmeService
├── git/
│   └── git_manager.py           # GitManager
├── models/
│   └── submission.py            # LeetCodeProblem, SubmissionCode
├── utils/
│   ├── logger.py                # setup_logger
│   ├── config.py                # AppConfig
│   ├── exceptions.py            # Custom exceptions
│   ├── resume_state.py          # ResumeState, ResumeCheckpoint
│   └── wait.py                  # Selenium helpers
├── main.py                      # Entry point
├── config.yaml                  # Configuration
├── requirements.txt             # Dependencies
└── .gitignore
```

## SOLID & Design Principles

- **Single Responsibility** - Each module has a single, well-defined purpose
- **Open/Closed** - Easy to extend with new exporters or crawlers
- **Liskov Substitution** - Service classes follow consistent interfaces
- **Interface Segregation** - Minimal dependencies between modules
- **Dependency Inversion** - High-level modules depend on abstractions

## Dependencies

- `selenium` - Web automation
- `webdriver-manager` - Automatic Chrome driver management
- `GitPython` - Git operations
- `rich` - Beautiful console output
- `tqdm` - Progress bars
- `PyYAML` - Config file parsing

## Logging

Logs are written to both console (with colors via Rich) and file (`leetcode_exporter.log`).

Configure log level in `config.yaml`:
```yaml
log_level: DEBUG    # More verbose
log_level: INFO     # Normal
log_level: WARNING  # Errors only
```

## Troubleshooting

### Login fails
- Verify username and password in `config.yaml`
- Check if LeetCode has enabled 2FA (may need to disable for automation)

### Page elements not found
- LeetCode may have updated their HTML structure
- Update CSS selectors in relevant crawler files

### Chrome driver issues
- `webdriver-manager` auto-downloads the correct driver
- Ensure Chrome/Chromium is installed

### Git push fails
- Verify SSH keys are configured for GitHub or use HTTPS
- Set `headless: false` to debug browser behavior

## Contributing

Feel free to extend the project with:
- Support for more languages
- Different export formats
- Cloud storage integration
- CI/CD integration

## License

MIT
