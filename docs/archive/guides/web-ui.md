# Web UI Guide

Access the Immigration Platform through a user-friendly web interface that runs locally on your device and network.

## Quick Start

### Installation

```bash
# Install Streamlit
pip install streamlit

# Or install all dependencies
pip install -r requirements.txt
```

### Launch

**Windows:**
```bash
# Double-click start-ui.bat
# Or run:
start-ui.bat
```

**Linux/Mac:**
```bash
# Make script executable (first time only)
chmod +x start-ui.sh

# Run
./start-ui.sh

# Or directly:
streamlit run app.py --server.address=0.0.0.0
```

### Access

**On your computer:**
- Open browser to: http://localhost:8501

**From other devices on your network:**
- Phone, tablet, other computers
- Use: http://YOUR-IP-ADDRESS:8501
- (The launch script shows your IP address)

## Features

### 1. Home Page (🏠)

**Overview of the platform:**
- Statistics (countries, visas, features)
- Key features explanation
- Quick start guide

### 2. Build Profile (👤)

**Create your immigration profile:**

**Fields:**
- Age (18-100)
- Education Level (High School → PhD)
- Years of Work Experience
- Occupation
- IELTS Score (if taken)
- Countries of Interest

**Actions:**
- Save profile
- View profile summary
- Profile saved to session (persists while app is open)

### 3. Find Visas (🔍)

**Match your profile to visas:**

**Features:**
- Shows top 10 matching visas
- Eligibility score for each visa
- Requirements breakdown
- Your strengths for each visa
- Gaps (what you're missing)
- Filtered by score (≥50% eligibility)

**Display:**
- Visa name and type
- Country
- Category (work, study, family, etc.)
- Detailed requirements
- Personalized feedback

### 4. AI Assistant (💬)

**Chat with AI about immigration:**

**Capabilities:**
- Ask about visa requirements
- Get application process information
- Compare visa options
- Understand eligibility criteria
- Get personalized answers

**Features:**
- Chat history (saved during session)
- Context-aware responses
- Uses enhanced hybrid search
- Sources from structured visa database

**Requirements:**
- OpenRouter or OpenAI API key
- Set in config.yaml or environment

### 5. Admin Tools (📊)

**Manage system and data:**

**Tabs:**

**Data Collection:**
- Trigger crawler for countries
- Run classifier to extract data
- (Recommended: use CLI for better control)

**System Status:**
- View raw data file count
- View structured data file count
- Check service availability
- System health monitoring

**Statistics:**
- Visas by country
- Visas by category
- Total visa count
- Data distribution

## Usage Flow

### First-Time Setup

1. **Prepare Data:**
   ```bash
   # Crawl government websites
   python main.py crawl --countries australia canada

   # Extract and structure data
   python main.py classify --all
   ```

2. **Set Up AI (optional):**
   ```bash
   # Get free API key from https://openrouter.ai/keys
   # Windows:
   $env:OPENROUTER_API_KEY = 'your-key-here'

   # Linux/Mac:
   export OPENROUTER_API_KEY='your-key-here'
   ```

3. **Launch UI:**
   ```bash
   ./start-ui.sh      # Linux/Mac
   start-ui.bat       # Windows
   ```

### Normal Usage

1. **Launch UI** → Open http://localhost:8501
2. **Build Profile** → Fill in your details → Save
3. **Find Visas** → Click "Find Matching Visas" → Review results
4. **Ask Questions** → Go to AI Assistant → Chat about visas
5. **Compare** → Switch between matched visas
6. **Apply** → Use source URLs to official pages

## Network Access

### Allow Access from Other Devices

The UI runs on `0.0.0.0:8501` which allows network access.

**Find your IP address:**

**Windows:**
```bash
ipconfig
# Look for IPv4 Address: 192.168.x.x
```

**Linux/Mac:**
```bash
ifconfig
# Or
hostname -I
```

**Access from other devices:**
```
http://192.168.1.100:8501
# (Replace with your actual IP)
```

### Firewall Settings

**Windows Firewall:**
1. Allow Python through firewall
2. Or allow port 8501

**Linux:**
```bash
# UFW
sudo ufw allow 8501

# Firewalld
sudo firewall-cmd --add-port=8501/tcp
```

## Configuration

### Change Port

Edit launch script or run:

```bash
streamlit run app.py --server.port=8080
```

### Change Host

**Localhost only (more secure):**
```bash
streamlit run app.py --server.address=localhost
```

**Network access:**
```bash
streamlit run app.py --server.address=0.0.0.0
```

### Theme

Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1E88E5"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F5F5F5"
textColor = "#262730"
font = "sans serif"
```

## Troubleshooting

### Issue: Port Already in Use

**Error:**
```
Address already in use
```

**Solution:**
```bash
# Change port
streamlit run app.py --server.port=8502

# Or kill existing process (Windows)
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8501
kill <PID>
```

### Issue: Cannot Access from Network

**Symptoms:**
- Works on localhost
- Doesn't work on phone/tablet

**Solutions:**
1. Check firewall allows port 8501
2. Ensure running with --server.address=0.0.0.0
3. Verify devices on same network
4. Use IP address, not hostname

### Issue: AI Assistant Not Working

**Error:**
```
API key not set
```

**Solution:**
1. Check API key in config.yaml
2. Or set environment variable:
   ```bash
   # Windows
   $env:OPENROUTER_API_KEY = 'sk-or-v1-...'

   # Linux/Mac
   export OPENROUTER_API_KEY='sk-or-v1-...'
   ```

### Issue: No Visa Matches Found

**Cause:**
- No structured data

**Solution:**
```bash
python main.py classify --all
```

### Issue: UI is Slow

**Causes:**
- Large dataset
- Complex queries
- First-time indexing

**Solutions:**
1. Wait for initial indexing (1-2 min, one-time)
2. Reduce max_visas in config
3. Use faster computer if possible

## Advanced Usage

### Custom Styling

Edit `app.py` CSS section:

```python
st.markdown("""
<style>
    .main-header {
        color: #YOUR_COLOR;  # Change this
    }
</style>
""", unsafe_allow_html=True)
```

### Add New Pages

In `app.py`:

```python
def main():
    page = st.sidebar.radio(
        "Navigation",
        ["Home", "Profile", "Visas", "Chat", "Admin", "NEW PAGE"]  # Add here
    )

    if page == "NEW PAGE":
        show_new_page()  # Create this function

def show_new_page():
    st.title("New Page")
    # Your content here
```

### Session State

Data persists during session:

```python
# Save data
st.session_state['key'] = value

# Retrieve data
value = st.session_state.get('key', default)

# Check if exists
if 'key' in st.session_state:
    # Do something
```

## Performance Tips

1. **Cache Data:**
   ```python
   @st.cache_data
   def load_visas():
       # Expensive operation
       return data
   ```

2. **Lazy Loading:**
   - UI only loads AI models when needed
   - Embeddings cached after first use

3. **Limit Results:**
   - Top 10 visas shown by default
   - Adjust in code if needed

## Security Notes

### Running on Network

**Risks:**
- Anyone on your network can access
- No authentication by default

**Mitigations:**
1. **Use localhost only** (no network access):
   ```bash
   streamlit run app.py --server.address=localhost
   ```

2. **Use VPN** for remote access

3. **Firewall rules** to limit access

4. **Don't expose to internet** without authentication

### API Keys

- **Never commit** API keys to git
- **Use environment variables** or config
- **Don't share** config.yaml with keys

## Deployment Options

### Local Network (Current)

✅ Works out of the box
✅ Fast and private
❌ Only accessible on your network

### Cloud Deployment (Future)

**Options:**
- Streamlit Cloud (free for public apps)
- Heroku
- AWS/Google Cloud
- DigitalOcean

**Requires:**
- Authentication system
- Database (not JSON files)
- Security hardening

## See Also

- [Quick Start Guide](quick-start.md) - CLI usage
- [Configuration Guide](configuration.md) - System configuration
- [Assistant Documentation](../services/assistant.md) - AI features
- [Troubleshooting](../troubleshooting.md) - Common issues

---

**Launch now:**

```bash
./start-ui.sh       # Linux/Mac
start-ui.bat        # Windows
```

Then open: http://localhost:8501 🚀
