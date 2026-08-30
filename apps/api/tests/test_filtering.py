from app.core.filtering import is_file_allowed

def test_filtering_directories():
    assert not is_file_allowed("node_modules/express/index.js")
    assert not is_file_allowed("dist/bundle.js")
    assert not is_file_allowed("build/index.html")
    assert not is_file_allowed(".git/config")
    
    # Valid directories
    assert is_file_allowed("src/components/button.tsx")
    assert is_file_allowed("app/main.py")

def test_filtering_extensions():
    assert not is_file_allowed("assets/logo.png")
    assert not is_file_allowed("docs/spec.pdf")
    assert not is_file_allowed("backend/app.exe")
    assert not is_file_allowed("keys/private.pem")
    
    # Valid extensions
    assert is_file_allowed("README.md")
    assert is_file_allowed("utils/math.ts")

def test_filtering_specific_files():
    assert not is_file_allowed(".env")
    assert not is_file_allowed("config/.env.local")
    assert not is_file_allowed("package-lock.json")
    
    # Valid but similarly named files
    assert is_file_allowed("package.json")
    assert is_file_allowed("config.env.js") # This is fine, extension is .js
    assert is_file_allowed("env.example") # This is fine too
