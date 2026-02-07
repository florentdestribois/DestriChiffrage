# Modifications finales pour compléter l'implémentation du devis rapide

## ✅ Déjà fait
1. CartManager créé (`src/cart_manager.py`)
2. CartPanel créé (`src/ui/cart_panel.py`)
3. CartExportDialog créé (`src/ui/cart_export_dialog.py`)
4. Méthodes database.py ajoutées (export_cart_to_csv, etc.)
5. Imports ajoutés dans main_window.py
6. Colonne 'cart' ajoutée au Treeview
7. Initialisation CartManager dans __init__

## ⏳ Modifications restantes dans main_window.py

### 1. Ajouter bouton Devis rapide dans la toolbar (après ligne ~300)

Ajouter dans `_create_toolbar()` :

```python
# Bouton Devis rapide
self.cart_btn = tk.Button(action_buttons, text="\U0001F6D2 Devis rapide (0)",  # 🛒
                          font=Theme.FONTS['body_bold'],
                          bg=Theme.COLORS['secondary'], fg=Theme.COLORS['white'],
                          activebackground=Theme.COLORS['accent'],
                          bd=0, padx=12, pady=6, cursor='hand2',
                          command=self._show_cart_panel)
self.cart_btn.pack(side=tk.LEFT, padx=4)
```

### 2. Modifier _clear_pdf_icons() pour inclure cart (ligne ~948)

```python
def _clear_pdf_icons(self):
    """Nettoie toutes les icônes affichées (PDF, Devis et Devis rapide)"""
    for label in self.pdf_labels:
        try:
            label.place_forget()
            label.destroy()
        except:
            pass
    self.pdf_labels.clear()

    for label in self.devis_labels:
        try:
            label.place_forget()
            label.destroy()
        except:
            pass
    self.devis_labels.clear()

    for label in self.cart_labels:
        try:
            label.place_forget()
            label.destroy()
        except:
            pass
    self.cart_labels.clear()
```

### 3. Modifier _update_all_icons() (ligne ~970)

```python
def _update_all_icons(self):
    """Met à jour toutes les icônes (PDF, Devis et Devis rapide)"""
    self._update_pdf_icons()
    self._update_devis_icons()
    self._update_cart_icons()
```

### 4. Ajouter _update_cart_icons() (après ligne ~1065)

```python
def _update_cart_icons(self):
    """Met à jour les positions des icônes Devis rapide avec des Labels overlay"""
    # Obtenir les limites du Treeview
    try:
        tree_height = self.tree.winfo_height()
        tree_width = self.tree.winfo_width()
    except:
        return

    # Obtenir la colonne Cart (index 11)
    try:
        # Parcourir les items visibles
        for item in self.tree.get_children():
            bbox = self.tree.bbox(item, 'cart')
            if bbox:  # Item visible
                # Vérifier que la cellule est bien dans les limites
                if bbox[1] < 0 or bbox[1] + bbox[3] > tree_height:
                    continue
                if bbox[0] < 0 or bbox[0] + bbox[2] > tree_width:
                    continue

                # Vérifier si l'item est dans le devis rapide
                values = self.tree.item(item)['values']
                product_id = values[0]
                in_cart = self.cart_manager.is_in_cart(product_id)

                # Créer un label avec l'icône (emoji ou texte)
                x = bbox[0] + (bbox[2] - 24) // 2
                y = bbox[1] + (bbox[3] - 24) // 2 + 1

                # Emoji différent selon si dans devis rapide ou non
                emoji = "✓" if in_cart else "+"
                color = Theme.COLORS['success'] if in_cart else Theme.COLORS['secondary']

                label = tk.Label(self.tree.master, text=emoji,
                                font=('Segoe UI', 12, 'bold'),
                                bg='white', fg=color,
                                cursor='hand2', bd=0, relief='flat')
                label.place(x=x, y=y, width=24, height=24)

                # Bind pour ajouter/retirer au clic
                label.bind('<Button-1>', lambda e, i=item: self._on_cart_icon_click(i))

                self.cart_labels.append(label)

    except Exception as e:
        pass
```

### 5. Ajouter les méthodes de gestion du devis rapide (fin du fichier)

```python
def _on_cart_icon_click(self, item):
    """Gère le clic sur une icône Devis rapide"""
    values = self.tree.item(item)['values']
    product_id = values[0]

    # Récupérer le produit complet
    produits = self.db.search_produits()
    product = next((p for p in produits if p['id'] == product_id), None)

    if not product:
        return

    if self.cart_manager.is_in_cart(product_id):
        # Retirer du devis rapide
        self.cart_manager.remove_from_cart(product_id)
        self.set_status(f"Article retiré du devis rapide: {product['designation']}")
    else:
        # Ajouter au devis rapide
        self.cart_manager.add_to_cart(product)
        self.set_status(f"Article ajouté au devis rapide: {product['designation']}")

    # Rafraîchir l'affichage
    self._update_cart_button()
    self._update_all_icons()

def _update_cart_button(self):
    """Met à jour le compteur du bouton devis rapide"""
    count = self.cart_manager.get_cart_count()
    self.cart_btn.config(text=f"\U0001F6D2 Devis rapide ({count})")

def _show_cart_panel(self):
    """Affiche le panneau du devis rapide"""
    CartPanel(self.root, self.cart_manager, self.db,
             on_export_callback=self._on_export_cart)

def _on_export_cart(self):
    """Lance l'export du devis rapide"""
    dialog = CartExportDialog(self.root, self.cart_manager, self.db)
    self.root.wait_window(dialog)

    if dialog.result:
        # Vider le devis rapide après export réussi
        response = messagebox.askyesno(
            "Vider le devis rapide",
            "Export terminé avec succès!\n\nVoulez-vous vider le devis rapide?"
        )
        if response:
            self.cart_manager.clear_cart()
            self._update_cart_button()
            self.on_search()  # Rafraîchir pour mettre à jour les icônes
```

## Test rapide

Pour tester sans tout intégrer :
```bash
cd "C:\Users\tt\Documents\Developpement logiciel\DestriChiffrage"
python src/main.py
```

Vérifier :
1. Le bouton "Devis rapide (0)" apparaît
2. Les icônes "+" apparaissent dans la colonne Devis rapide
3. Clic sur "+" ajoute au devis rapide → devient "✓"
4. Le compteur du bouton s'incrémente
5. Clic sur bouton Devis rapide ouvre la fenêtre
6. Export fonctionne avec les options

## Notes

- Les icônes utilisent des emojis Unicode (🛒, +, ✓) au lieu d'images PNG
- Couleur verte (✓) pour "dans le devis rapide", or (+) pour "ajouter"
- Le devis rapide persiste pendant la session mais pas entre les redémarrages
