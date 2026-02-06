"""
Script de test pour l'auto-updater avec interface
"""
import sys
import os

# Ajouter src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from tkinter import messagebox

def test_updater_function():
    """Test de la fonction updater seule"""
    print("\n=== Test 1: Updater seul ===")
    try:
        from updater import Updater
        updater = Updater()
        print(f"Version actuelle: {updater.current_version}")

        print("Vérification des mises à jour...")
        result = updater.check_for_updates()
        print(f"Résultat: {result}")

        if result.get('error'):
            print(f"❌ Erreur: {result['error']}")
        elif result.get('available'):
            print(f"✅ Mise à jour disponible: {result['latest_version']}")
        else:
            print("ℹ️ Aucune mise à jour")

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

def test_dialog():
    """Test du dialogue de mise à jour"""
    print("\n=== Test 2: Dialogue UI ===")

    root = tk.Tk()
    root.title("Test Auto-Updater")
    root.geometry("400x200")

    status_label = tk.Label(root, text="Prêt pour le test", pady=20)
    status_label.pack()

    def on_check_updates():
        """Simule le clic sur Vérifier les mises à jour"""
        status_label.config(text="Vérification en cours...")
        root.update()

        try:
            from updater import Updater
            updater = Updater()
            result = updater.check_for_updates()

            print(f"Résultat de la vérification: {result}")

            if result.get('error'):
                status_label.config(text=f"Erreur: {result['error']}")
                messagebox.showerror("Erreur", f"Erreur:\n{result['error']}")
            elif result.get('available'):
                status_label.config(text=f"Mise à jour {result['latest_version']} disponible!")

                # Tester le dialogue UpdateDialog
                try:
                    from ui.update_dialog import UpdateDialog
                    dialog = UpdateDialog(root, result)
                    status_label.config(text="Dialogue de mise à jour ouvert")
                except Exception as e:
                    status_label.config(text=f"Erreur dialogue: {e}")
                    print(f"Erreur UpdateDialog: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                status_label.config(text="Aucune mise à jour disponible")
                messagebox.showinfo("Aucune mise à jour",
                                   "Vous utilisez déjà la dernière version.")

        except Exception as e:
            status_label.config(text=f"Exception: {e}")
            messagebox.showerror("Exception", str(e))
            print(f"Exception: {e}")
            import traceback
            traceback.print_exc()

    btn = tk.Button(root, text="Vérifier les mises à jour",
                    command=on_check_updates, padx=20, pady=10)
    btn.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    print("=" * 60)
    print("TEST AUTO-UPDATER DESTRICHIFFRAGE")
    print("=" * 60)

    # Test 1: Fonction seule
    test_updater_function()

    # Test 2: Interface graphique
    print("\n" + "=" * 60)
    print("Lancement de l'interface de test...")
    print("Cliquez sur le bouton pour tester la vérification")
    print("=" * 60 + "\n")

    test_dialog()
