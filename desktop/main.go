// Redstone Planner pour Windows : un seul .exe qui contient le planificateur.
// Au lancement, il copie la page dans %LOCALAPPDATA%\RedstonePlanner et l'ouvre
// dans sa propre fenêtre (Microsoft Edge ou Chrome en mode application).
// Les circuits enregistrés restent d'un lancement à l'autre.
package main

import (
	"bytes"
	_ "embed"
	"net/url"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"syscall"
	"unsafe"
)

//go:embed redstone-planner.html
var page []byte

func main() {
	base := os.Getenv("LOCALAPPDATA")
	if base == "" {
		base = os.TempDir()
	}
	dir := filepath.Join(base, "RedstonePlanner")
	if err := os.MkdirAll(dir, 0o755); err != nil {
		fail("Impossible de créer le dossier " + dir + " : " + err.Error())
	}
	file := filepath.Join(dir, "redstone-planner.html")
	if old, err := os.ReadFile(file); err != nil || !bytes.Equal(old, page) {
		if err := os.WriteFile(file, page, 0o644); err != nil {
			fail("Impossible d'écrire " + file + " : " + err.Error())
		}
	}
	u := (&url.URL{Scheme: "file", Path: "/" + filepath.ToSlash(file)}).String()

	// Fenêtre d'application : Edge (présent sur Windows 10 et 11), sinon Chrome
	pf, pf86, local := os.Getenv("ProgramFiles"), os.Getenv("ProgramFiles(x86)"), os.Getenv("LOCALAPPDATA")
	browsers := []string{
		filepath.Join(pf86, `Microsoft\Edge\Application\msedge.exe`),
		filepath.Join(pf, `Microsoft\Edge\Application\msedge.exe`),
		filepath.Join(pf, `Google\Chrome\Application\chrome.exe`),
		filepath.Join(pf86, `Google\Chrome\Application\chrome.exe`),
		filepath.Join(local, `Google\Chrome\Application\chrome.exe`),
	}
	profile := filepath.Join(dir, "profil")
	for _, b := range browsers {
		if b == "" || strings.HasPrefix(b, `\`) {
			continue
		}
		if _, err := os.Stat(b); err == nil {
			cmd := exec.Command(b, "--app="+u, "--user-data-dir="+profile, "--no-first-run", "--no-default-browser-check",
				"--window-size=1400,900", "--disable-features=Translate")
			if cmd.Start() == nil {
				return
			}
		}
	}
	// Sinon : le navigateur par défaut
	if exec.Command("rundll32", "url.dll,FileProtocolHandler", u).Start() != nil {
		fail("Aucun navigateur trouvé. Ouvre ce fichier à la main :\n" + file)
	}
}

func fail(msg string) {
	user32 := syscall.NewLazyDLL("user32.dll")
	t, _ := syscall.UTF16PtrFromString(msg)
	c, _ := syscall.UTF16PtrFromString("Redstone Planner")
	user32.NewProc("MessageBoxW").Call(0, uintptr(unsafe.Pointer(t)), uintptr(unsafe.Pointer(c)), 0x10)
	os.Exit(1)
}
