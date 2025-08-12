# 🔐 PyPI Authentication Troubleshooting Guide

## ❌ **Current Issue: 403 Forbidden Error**

### **Error Message**
```
403 Invalid or non-existent authentication information. See https://pypi.org/help/#invalid-auth for more information.
```

## 🔍 **Common Causes and Solutions**

### **1. Token Format Issues**

#### **Problem**: Incorrect token format
PyPI tokens must start with `pypi-` and be the complete token.

#### **Solution**: Verify token format
```bash
# Your token should look like this:
pypi-AgEIcHlwaS5vcmcCJDIxNTg0Y2ZhLWNkZGItNGIzOC1hYzgyLWU4MTVmZTU2ZmM0NgACKlszLCIyMzFkYTE5ZS1lNjJiLTRjZjQtYjRkMy1lMTI5YTRkOTBmMjkiXQAABiDR_f8O2NzYklNHEVtK5xJm_o06w_nIZ_WuPNKvB0fyvwsource
```

### **2. Token Scope Issues**

#### **Problem**: Token doesn't have upload permissions
The token might not have the correct scope for uploading packages.

#### **Solution**: Check token scope
1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Navigate to "API tokens"
3. Check if your token has "Entire account" scope
4. If not, create a new token with "Entire account" scope

### **3. Package Name Ownership**

#### **Problem**: You don't own the package name
You might not have permission to upload to the `cloudbulkupload` package.

#### **Solution**: Verify package ownership
1. Go to [PyPI Package Page](https://pypi.org/project/cloudbulkupload/)
2. Check if you're listed as an owner/maintainer
3. If not, contact the current owner to add you

### **4. Token Expiration**

#### **Problem**: Token has expired
PyPI tokens can expire or be revoked.

#### **Solution**: Create a new token
1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Delete the old token
3. Create a new token with "Entire account" scope

### **5. Account Verification**

#### **Problem**: Account not verified
Your PyPI account might not be fully verified.

#### **Solution**: Verify your account
1. Check your email for verification links
2. Complete any pending verification steps
3. Ensure your account is active

## 🛠️ **Step-by-Step Troubleshooting**

### **Step 1: Verify Token Format**
```bash
# Check if your token starts with pypi-
echo "Your token should start with: pypi-"
```

### **Step 2: Test Token with curl**
```bash
# Test your token (replace YOUR_TOKEN with your actual token)
curl -H "Authorization: token YOUR_TOKEN" https://pypi.org/pypi/cloudbulkupload/json
```

### **Step 3: Check Package Ownership**
```bash
# Check if you can access the package
curl https://pypi.org/pypi/cloudbulkupload/json
```

### **Step 4: Verify Account Status**
1. Log into [PyPI](https://pypi.org)
2. Check account settings
3. Verify email is confirmed

## 🔧 **Alternative Solutions**

### **Solution 1: Use .pypirc File**
Create a `.pypirc` file in your project root:

```ini
[pypi]
username = __token__
password = pypi-YOUR_ACTUAL_TOKEN_HERE
```

### **Solution 2: Use Environment Variables**
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR_ACTUAL_TOKEN_HERE
twine upload dist/*
```

### **Solution 3: Use Keyring**
```bash
# Store credentials in keyring
keyring set https://upload.pypi.org/legacy/ __token__
# Enter your token when prompted
```

## 🚨 **Important Notes**

### **Token Security**
- Never commit tokens to version control
- Use environment variables or keyring for security
- Rotate tokens regularly

### **Package Name Conflicts**
- Ensure you own the package name
- Check for similar package names
- Consider using a different package name if needed

### **Rate Limiting**
- PyPI has rate limits
- Wait a few minutes between upload attempts
- Don't spam upload requests

## 📋 **Checklist**

- [ ] Token starts with `pypi-`
- [ ] Token has "Entire account" scope
- [ ] You own the package name
- [ ] Account is verified
- [ ] Token is not expired
- [ ] Using correct username (`__token__`)
- [ ] Package name is available

## 🔗 **Useful Links**

- [PyPI Account Settings](https://pypi.org/manage/account/)
- [PyPI API Tokens](https://pypi.org/help/#apitoken)
- [PyPI Upload Documentation](https://packaging.python.org/guides/distributing-packages-using-setuptools/#uploading-your-project-to-pypi)
- [PyPI Authentication Help](https://pypi.org/help/#invalid-auth)

---

**Issue**: 403 Forbidden - Invalid authentication  
**Status**: 🔍 **INVESTIGATING**  
**Next Step**: Verify token format and scope
