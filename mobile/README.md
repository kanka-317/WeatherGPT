# WeatherGPT Mobile Client (SIH PS 26068)

Flutter client for **WeatherGPT — AI-Driven Meteorological Intelligence & Disaster Early-Warning System**.

---

## 🛠️ Free Distribution Builds

### 1. Build Signed Android APK
Run from within the `mobile/` directory:
```bash
flutter pub get
flutter build apk --release --dart-define=BACKEND_URL=https://weathergpt-backend.onrender.com
```
The output file is generated at:
`mobile/build/app/outputs/flutter-apk/app-release.apk`

Rename this file to:
`WeatherGPT_PS26068_v1.0.0.apk`

### 2. Host on GitHub Releases (Free Tier APK Distribution)
1. Go to your GitHub repository &rarr; **Releases** &rarr; **Draft a new release**.
2. Set tag to `v1.0.0` (or your version).
3. Title: `WeatherGPT Mobile v1.0.0 (SIH PS 26068)`.
4. Drag and drop `WeatherGPT_PS26068_v1.0.0.apk` into the release binaries box.
5. Click **Publish release**. Evaluators and users can now directly download and sideload the APK onto any Android phone with zero Play Store fee.

### 3. Build Flutter Web Fallback (Zero-Install Browser Access)
For evaluators or judges on iOS or desktop without an Android test device:
```bash
flutter build web --release --dart-define=BACKEND_URL=https://weathergpt-backend.onrender.com
```
Deploy the resulting `mobile/build/web` folder to Netlify, Vercel, or GitHub Pages.

---

## ⚡ Automated CI/CD
A GitHub Actions workflow is pre-configured at [`.github/workflows/mobile_release.yml`](../.github/workflows/mobile_release.yml).
Whenever you push a tag (`git tag v1.0.0 && git push origin v1.0.0`) or click **Run workflow** under the GitHub Actions tab, it compiles both the APK and Web fallback automatically in the cloud and attaches the APK to GitHub Releases.
