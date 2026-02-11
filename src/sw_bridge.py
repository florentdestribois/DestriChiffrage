# -*- coding: utf-8 -*-
"""
DestriChiffrage - Module SolidWorks Bridge (sw_bridge.py)
=========================================================
Pont entre SolidWorks/SWOOD et la base de donnees DestriChiffrage.

Permet de :
- Lire/ecrire les proprietes personnalisees SolidWorks via COM API
- Synchroniser les quincailleries (Hardware) avec catalogue.db
- Recuperer les references fournisseur depuis la BDD pour les injecter dans SolidWorks
- Generer des commandes fournisseur depuis un assemblage SWOOD

Prerequis:
- pywin32 (pip install pywin32) pour l'acces COM a SolidWorks
- SolidWorks doit etre ouvert et un document actif

Auteur: DestriChiffrage / Destribois
Date: Fevrier 2026
"""

import os
import sys
import json
import csv
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any

# Logger
logger = logging.getLogger(__name__)

# =====================================================================
# CONSTANTES - Mapping entre proprietes SolidWorks et champs catalogue.db
# =====================================================================

# Proprietes personnalisees SWOOD pour les quincailleries (TypedObject HA)
# Ces noms correspondent exactement a ceux definis dans Report de travail.Cfg
SWCP_MAPPING = {
    # Propriete SW          ->  Champ catalogue.db
    'Code':                 'reference',        # Code/reference du produit
    'Supplier':             'fournisseur',       # Nom du fournisseur
    'Supplier_Reference':   'reference',        # Reference fournisseur (variante)
    'Cost':                 'prix_achat',        # Cout unitaire HT
    'FOURNISSEUR':          'fournisseur',       # Fournisseur (variante francaise)
    'DESCRIPTION':          'designation',       # Description du composant
    'FINISH':               'notes',             # Finition
}

# Proprietes supplementaires utiles pour les panneaux/produits (TypedObject TO_PRODUCT)
SWCP_PRODUCT_MAPPING = {
    'Width':                'largeur',
    'Depth':                'dimensions',        # Profondeur -> stockee dans dimensions
    'Height':               'hauteur',
    'PRODUCT_DESC':         'designation',
    'TYPE_CAISSON':         'sous_categorie',
    'NOM_CAISSON':          'designation',
}

# Types SWOOD reconnus
SWOOD_TYPES = {
    'HARDWARE': 'Quincaillerie',
    'NOT_HARDWARE': 'Non-quincaillerie',
    'PANEL': 'Panneau',
}

# Nom de la categorie par defaut dans DestriChiffrage pour les quincailleries SWOOD
DEFAULT_HARDWARE_CATEGORY = 'QUINCAILLERIE SWOOD'


# =====================================================================
# CLASSE PRINCIPALE - SolidWorksBridge
# =====================================================================

class SolidWorksBridge:
    """
    Pont entre SolidWorks COM API et DestriChiffrage.

    Permet de lire et ecrire les proprietes personnalisees SolidWorks,
    et de les synchroniser avec la base de donnees catalogue.db.
    """

    def __init__(self, database=None):
        """
        Initialise le bridge.

        Args:
            database: Instance de Database (si None, cree une nouvelle connexion)
        """
        self.sw_app = None
        self.sw_model = None
        self.connected = False
        self.db = database
        self._log = []  # Journal des operations

    # =================================================================
    # CONNEXION SOLIDWORKS
    # =================================================================

    def connect_solidworks(self) -> bool:
        """
        Se connecte a l'instance SolidWorks en cours d'execution.

        Returns:
            True si connecte avec succes, False sinon
        """
        try:
            import win32com.client

            # Tenter de se connecter a SolidWorks en cours d'execution
            self.sw_app = win32com.client.Dispatch("SldWorks.Application")

            if self.sw_app is None:
                self._add_log("ERREUR", "Impossible de se connecter a SolidWorks")
                return False

            # Verifier qu'un document est ouvert
            self.sw_model = self.sw_app.ActiveDoc
            if self.sw_model is None:
                self._add_log("AVERTISSEMENT", "SolidWorks connecte mais aucun document ouvert")
                self.connected = True
                return True

            doc_title = self.sw_model.GetTitle()
            self._add_log("INFO", f"Connecte a SolidWorks - Document: {doc_title}")
            self.connected = True
            return True

        except ImportError:
            self._add_log("ERREUR", "Module pywin32 non installe. Installer avec: pip install pywin32")
            return False
        except Exception as e:
            self._add_log("ERREUR", f"Erreur de connexion SolidWorks: {str(e)}")
            return False

    def get_active_document(self) -> Optional[str]:
        """
        Retourne le titre du document actif.

        Returns:
            Titre du document ou None
        """
        if not self.connected or self.sw_app is None:
            return None

        self.sw_model = self.sw_app.ActiveDoc
        if self.sw_model is None:
            return None

        return self.sw_model.GetTitle()

    # =================================================================
    # LECTURE PROPRIETES PERSONNALISEES
    # =================================================================

    def get_custom_property(self, property_name: str, config_name: str = "") -> Optional[str]:
        """
        Lit une propriete personnalisee du document actif.

        Args:
            property_name: Nom de la propriete (ex: 'Code', 'Supplier', 'Cost')
            config_name: Nom de la configuration (vide = config active)

        Returns:
            Valeur de la propriete (str) ou None si non trouvee
        """
        if not self.connected or self.sw_model is None:
            self._add_log("ERREUR", "Pas de document actif pour lire les proprietes")
            return None

        try:
            # Constantes SolidWorks pour CustomPropertyManager
            # swCustomInfoText = 30 (texte)
            # swCustomInfoNumber = 3 (nombre)

            ext = self.sw_model.Extension
            if config_name:
                cpm = ext.CustomPropertyManager(config_name)
            else:
                cpm = ext.CustomPropertyManager("")

            if cpm is None:
                return None

            # Get2 retourne (retval, val_out, resolved_val_out, was_resolved)
            # Methode recommandee depuis SolidWorks 2018+
            ret = cpm.Get5(property_name, False)
            # ret = (retval, val_out, resolved_val_out, was_resolved, link_to_property)

            if ret[0] == 0:  # swCustomInfoGetResult_NotPresent
                return None

            # Retourner la valeur resolue (index 2)
            resolved_value = ret[2] if len(ret) > 2 else ret[1]
            return str(resolved_value) if resolved_value else None

        except Exception as e:
            self._add_log("ERREUR", f"Erreur lecture propriete '{property_name}': {str(e)}")
            return None

    def set_custom_property(self, property_name: str, value: str,
                           config_name: str = "", value_type: int = 30) -> bool:
        """
        Ecrit une propriete personnalisee dans le document actif.

        Args:
            property_name: Nom de la propriete
            value: Valeur a ecrire
            config_name: Configuration cible (vide = config active)
            value_type: Type de propriete (30=texte, 3=nombre, 11=oui/non, 64=date)

        Returns:
            True si ecrit avec succes
        """
        if not self.connected or self.sw_model is None:
            self._add_log("ERREUR", "Pas de document actif pour ecrire les proprietes")
            return False

        try:
            ext = self.sw_model.Extension
            cpm = ext.CustomPropertyManager(config_name if config_name else "")

            if cpm is None:
                return False

            # Tenter de modifier la propriete existante
            # Add3(FieldName, FieldType, FieldValue, OverwriteExisting)
            # swCustomInfoType_e: Text=30, Number=3, YesOrNo=11, Date=64
            result = cpm.Add3(property_name, value_type, str(value), 1)  # 1 = overwrite

            # result: 0=OK, 1=AlreadyExists(updated), 2=GenericError
            if result in (0, 1):
                self._add_log("INFO", f"Propriete '{property_name}' = '{value}'")
                return True
            else:
                self._add_log("ERREUR", f"Echec ecriture propriete '{property_name}' (code: {result})")
                return False

        except Exception as e:
            self._add_log("ERREUR", f"Erreur ecriture propriete '{property_name}': {str(e)}")
            return False

    def get_all_custom_properties(self, config_name: str = "") -> Dict[str, str]:
        """
        Lit toutes les proprietes personnalisees du document actif.

        Args:
            config_name: Configuration (vide = defaut)

        Returns:
            Dictionnaire {nom_propriete: valeur}
        """
        properties = {}

        if not self.connected or self.sw_model is None:
            return properties

        try:
            ext = self.sw_model.Extension
            cpm = ext.CustomPropertyManager(config_name if config_name else "")

            if cpm is None:
                return properties

            # GetNames retourne un tuple des noms de proprietes
            names = cpm.GetNames()
            if names is None:
                return properties

            for name in names:
                val = self.get_custom_property(name, config_name)
                if val is not None:
                    properties[name] = val

            return properties

        except Exception as e:
            self._add_log("ERREUR", f"Erreur lecture proprietes: {str(e)}")
            return properties

    # =================================================================
    # TRAVERSEE D'ASSEMBLAGE - Extraction quincailleries
    # =================================================================

    def traverse_assembly(self, include_hardware_only: bool = True) -> List[Dict]:
        """
        Parcourt l'assemblage actif et extrait les composants (quincailleries).

        Cette methode traverse l'arbre d'assemblage SolidWorks et lit les
        proprietes personnalisees de chaque composant. C'est l'equivalent
        Python de ce que fait le Report SWOOD avec TypedObject HA.

        Args:
            include_hardware_only: Si True, ne retourne que les quincailleries

        Returns:
            Liste de dictionnaires contenant les infos de chaque composant
        """
        components = []

        if not self.connected or self.sw_model is None:
            self._add_log("ERREUR", "Pas de document actif")
            return components

        try:
            # Verifier que c'est un assemblage (type 2)
            doc_type = self.sw_model.GetType()
            if doc_type != 2:  # swDocASSEMBLY = 2
                self._add_log("ERREUR", "Le document actif n'est pas un assemblage")
                return components

            # Obtenir la configuration active
            config = self.sw_model.GetActiveConfiguration()
            if config is None:
                return components

            # Obtenir le composant racine
            root_component = config.GetRootComponent3(True)
            if root_component is None:
                return components

            # Traverser recursivement
            self._traverse_component(root_component, components, include_hardware_only, depth=0)

            self._add_log("INFO", f"Traversee terminee: {len(components)} composant(s) trouve(s)")
            return components

        except Exception as e:
            self._add_log("ERREUR", f"Erreur traversee assemblage: {str(e)}")
            return components

    def _traverse_component(self, component, results: List[Dict],
                           hardware_only: bool, depth: int):
        """
        Traverse recursivement un composant et ses enfants.

        Args:
            component: IComponent2 SolidWorks
            results: Liste accumulatrice des resultats
            hardware_only: Filtre quincailleries uniquement
            depth: Profondeur de recursion
        """
        try:
            # Obtenir le modele du composant
            comp_model = component.GetModelDoc2()
            if comp_model is None:
                return

            # Lire les proprietes personnalisees
            props = {}
            try:
                ext = comp_model.Extension
                cpm = ext.CustomPropertyManager("")

                if cpm is not None:
                    names = cpm.GetNames()
                    if names:
                        for name in names:
                            ret = cpm.Get5(name, False)
                            if ret and len(ret) > 2 and ret[2]:
                                props[name] = str(ret[2])
            except:
                pass

            # Determiner si c'est une quincaillerie
            swood_type = props.get('SWOOD_TYPE', '')
            comp_path = component.GetPathName()
            is_hardware = (
                swood_type == 'HARDWARE'
                or 'Hardwares' in (comp_path or '')
            ) and swood_type != 'NOT_HARDWARE'

            if not hardware_only or is_hardware:
                comp_info = {
                    'name': component.Name2,
                    'path': comp_path,
                    'is_hardware': is_hardware,
                    'swood_type': swood_type,
                    'depth': depth,
                    'properties': props,
                    # Champs cles pour le mapping vers catalogue.db
                    'code': props.get('Code', ''),
                    'supplier': props.get('Supplier', props.get('FOURNISSEUR', '')),
                    'supplier_reference': props.get('Supplier_Reference', ''),
                    'cost': self._parse_float(props.get('Cost', '0')),
                    'description': props.get('DESCRIPTION', component.Name2),
                    'finish': props.get('FINISH', ''),
                    'quantity': self._get_component_quantity(component),
                }
                results.append(comp_info)

            # Traverser les enfants
            children = component.GetChildren()
            if children:
                for child in children:
                    self._traverse_component(child, results, hardware_only, depth + 1)

        except Exception as e:
            self._add_log("AVERTISSEMENT",
                         f"Erreur sur composant (profondeur {depth}): {str(e)}")

    def _get_component_quantity(self, component) -> int:
        """Retourne la quantite d'instances d'un composant dans l'assemblage."""
        try:
            # GetSuppression2 retourne l'etat de suppression
            # On compte les instances non supprimees
            return 1  # Par defaut, la quantite est geree au niveau du Report SWOOD
        except:
            return 1

    # =================================================================
    # SYNCHRONISATION AVEC CATALOGUE.DB
    # =================================================================

    def sync_hardware_to_db(self, components: List[Dict] = None,
                           create_if_missing: bool = True,
                           update_prices: bool = True) -> Dict[str, int]:
        """
        Synchronise les quincailleries SolidWorks vers la base de donnees.

        Pour chaque quincaillerie :
        1. Cherche si elle existe dans catalogue.db (par reference/code)
        2. Si elle existe : met a jour le prix si necessaire
        3. Si elle n'existe pas : la cree dans la base

        Args:
            components: Liste des composants (si None, traverse l'assemblage)
            create_if_missing: Creer les produits absents de la BDD
            update_prices: Mettre a jour les prix si different

        Returns:
            Statistiques: {created, updated, skipped, errors}
        """
        if self.db is None:
            self._add_log("ERREUR", "Aucune base de donnees connectee")
            return {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0}

        if components is None:
            components = self.traverse_assembly(include_hardware_only=True)

        stats = {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0}

        for comp in components:
            try:
                code = comp.get('code', '').strip()
                if not code:
                    stats['skipped'] += 1
                    continue

                # Chercher par reference dans la BDD
                existing = self.db.search_produits(
                    terme=code,
                    categorie=DEFAULT_HARDWARE_CATEGORY,
                    actif_only=True,
                    limit=10
                )

                # Filtrer pour correspondance exacte de reference
                match = None
                for prod in existing:
                    if prod.get('reference', '').strip().upper() == code.strip().upper():
                        match = prod
                        break

                if match:
                    # Produit existant - mettre a jour si necessaire
                    if update_prices and comp.get('cost', 0) > 0:
                        if abs(match.get('prix_achat', 0) - comp['cost']) > 0.01:
                            self.db.update_produit(match['id'], {
                                'categorie': match.get('categorie', DEFAULT_HARDWARE_CATEGORY),
                                'sous_categorie': match.get('sous_categorie', ''),
                                'sous_categorie_2': match.get('sous_categorie_2', ''),
                                'sous_categorie_3': match.get('sous_categorie_3', ''),
                                'designation': match.get('designation', ''),
                                'description': match.get('description', ''),
                                'dimensions': match.get('dimensions', ''),
                                'hauteur': match.get('hauteur'),
                                'largeur': match.get('largeur'),
                                'prix_achat': comp['cost'],
                                'reference': match.get('reference', ''),
                                'fournisseur': comp.get('supplier', '') or match.get('fournisseur', ''),
                                'marque': match.get('marque', ''),
                                'chantier': match.get('chantier', ''),
                                'notes': match.get('notes', ''),
                                'fiche_technique': match.get('fiche_technique', ''),
                                'devis_fournisseur': match.get('devis_fournisseur', ''),
                            })
                            stats['updated'] += 1
                            self._add_log("INFO",
                                f"Prix mis a jour: {code} ({match['prix_achat']:.2f} -> {comp['cost']:.2f})")
                        else:
                            stats['skipped'] += 1
                    else:
                        stats['skipped'] += 1

                elif create_if_missing:
                    # Creer le produit
                    new_id = self.db.add_produit({
                        'categorie': DEFAULT_HARDWARE_CATEGORY,
                        'sous_categorie': comp.get('finish', ''),
                        'designation': comp.get('description', code),
                        'description': f"Import SolidWorks - {comp.get('name', '')}",
                        'prix_achat': comp.get('cost', 0),
                        'reference': code,
                        'fournisseur': comp.get('supplier', ''),
                        'notes': f"Import auto SWOOD {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                    })
                    stats['created'] += 1
                    self._add_log("INFO", f"Nouveau produit cree: {code} (ID: {new_id})")
                else:
                    stats['skipped'] += 1

            except Exception as e:
                stats['errors'] += 1
                self._add_log("ERREUR", f"Erreur sync composant '{comp.get('code', '?')}': {str(e)}")

        self._add_log("INFO",
            f"Synchronisation terminee: {stats['created']} crees, "
            f"{stats['updated']} mis a jour, {stats['skipped']} ignores, "
            f"{stats['errors']} erreurs")

        return stats

    def sync_db_to_solidworks(self, components: List[Dict] = None,
                              properties_to_update: List[str] = None) -> Dict[str, int]:
        """
        Synchronise les donnees DestriChiffrage vers les proprietes SolidWorks.

        Pour chaque quincaillerie dans l'assemblage :
        1. Cherche le produit correspondant dans catalogue.db (par code/reference)
        2. Ecrit les proprietes personnalisees dans le composant SolidWorks

        Cas d'usage principal: Recuperer les references fournisseur, prix a jour
        et informations depuis DestriChiffrage pour les injecter dans SolidWorks.

        Args:
            components: Liste des composants (si None, traverse l'assemblage)
            properties_to_update: Liste des proprietes a ecrire (None = toutes)
                Ex: ['Supplier', 'Cost', 'Supplier_Reference', 'FOURNISSEUR']

        Returns:
            Statistiques: {updated, not_found, skipped, errors}
        """
        if self.db is None:
            self._add_log("ERREUR", "Aucune base de donnees connectee")
            return {'updated': 0, 'not_found': 0, 'skipped': 0, 'errors': 0}

        if components is None:
            components = self.traverse_assembly(include_hardware_only=True)

        if properties_to_update is None:
            properties_to_update = ['Code', 'Supplier', 'Supplier_Reference', 'Cost', 'FOURNISSEUR']

        stats = {'updated': 0, 'not_found': 0, 'skipped': 0, 'errors': 0}

        for comp in components:
            try:
                code = comp.get('code', '').strip()
                if not code:
                    stats['skipped'] += 1
                    continue

                # Chercher dans la BDD
                existing = self.db.search_produits(terme=code, actif_only=True, limit=10)
                match = None
                for prod in existing:
                    if prod.get('reference', '').strip().upper() == code.strip().upper():
                        match = prod
                        break

                if not match:
                    stats['not_found'] += 1
                    self._add_log("AVERTISSEMENT", f"Produit non trouve dans BDD: {code}")
                    continue

                # Ouvrir le composant pour ecrire les proprietes
                comp_model = self._get_component_model(comp.get('name', ''))
                if comp_model is None:
                    stats['errors'] += 1
                    continue

                # Ecrire les proprietes
                updates = {}

                if 'Code' in properties_to_update:
                    updates['Code'] = match.get('reference', '')
                if 'Supplier' in properties_to_update:
                    updates['Supplier'] = match.get('fournisseur', '')
                if 'FOURNISSEUR' in properties_to_update:
                    updates['FOURNISSEUR'] = match.get('fournisseur', '')
                if 'Supplier_Reference' in properties_to_update:
                    updates['Supplier_Reference'] = match.get('reference', '')
                if 'Cost' in properties_to_update:
                    updates['Cost'] = str(match.get('prix_achat', 0))
                if 'DESCRIPTION' in properties_to_update:
                    updates['DESCRIPTION'] = match.get('designation', '')

                success = self._write_properties_to_component(comp_model, updates)
                if success:
                    stats['updated'] += 1
                    self._add_log("INFO", f"Proprietes mises a jour pour: {code}")
                else:
                    stats['errors'] += 1

            except Exception as e:
                stats['errors'] += 1
                self._add_log("ERREUR", f"Erreur ecriture SW pour '{comp.get('code', '?')}': {str(e)}")

        return stats

    def _get_component_model(self, component_name: str):
        """Obtient le ModelDoc2 d'un composant par son nom."""
        try:
            if self.sw_model is None:
                return None

            config = self.sw_model.GetActiveConfiguration()
            root = config.GetRootComponent3(True)
            children = root.GetChildren()

            if children:
                for child in children:
                    if child.Name2 == component_name:
                        return child.GetModelDoc2()
            return None
        except:
            return None

    def _write_properties_to_component(self, comp_model, properties: Dict[str, str]) -> bool:
        """Ecrit un dictionnaire de proprietes dans un composant."""
        try:
            ext = comp_model.Extension
            cpm = ext.CustomPropertyManager("")

            if cpm is None:
                return False

            for name, value in properties.items():
                # Type texte = 30, nombre = 3
                value_type = 3 if name == 'Cost' else 30
                cpm.Add3(name, value_type, str(value), 1)  # 1 = overwrite

            return True
        except Exception as e:
            self._add_log("ERREUR", f"Erreur ecriture proprietes composant: {str(e)}")
            return False

    # =================================================================
    # GENERATION COMMANDE FOURNISSEUR
    # =================================================================

    def generate_supplier_order(self, components: List[Dict] = None,
                                output_path: str = None,
                                group_by_supplier: bool = True) -> str:
        """
        Genere un fichier CSV de commande fournisseur depuis l'assemblage.

        Regroupe les quincailleries par fournisseur, cumule les quantites,
        et ajoute les prix depuis catalogue.db.

        Args:
            components: Liste des composants (si None, traverse l'assemblage)
            output_path: Chemin du fichier CSV de sortie
            group_by_supplier: Regrouper par fournisseur

        Returns:
            Chemin du fichier genere
        """
        if components is None:
            components = self.traverse_assembly(include_hardware_only=True)

        if not components:
            self._add_log("AVERTISSEMENT", "Aucune quincaillerie trouvee")
            return ""

        # Enrichir avec les donnees BDD si disponible
        enriched = self._enrich_from_db(components)

        # Agrouper par fournisseur et reference
        orders = {}
        for comp in enriched:
            supplier = comp.get('supplier', 'INCONNU') or 'INCONNU'
            code = comp.get('code', '') or comp.get('supplier_reference', '')

            if not code:
                continue

            key = f"{supplier}|{code}"
            if key not in orders:
                orders[key] = {
                    'fournisseur': supplier,
                    'reference': code,
                    'designation': comp.get('description', ''),
                    'prix_unitaire': comp.get('cost', 0),
                    'quantite': 0,
                    'prix_total': 0,
                }
            orders[key]['quantite'] += comp.get('quantity', 1)
            orders[key]['prix_total'] = orders[key]['quantite'] * orders[key]['prix_unitaire']

        # Trier par fournisseur puis reference
        sorted_orders = sorted(orders.values(), key=lambda x: (x['fournisseur'], x['reference']))

        # Generer le fichier CSV
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            doc_name = self.get_active_document() or "export"
            doc_name = doc_name.replace('.SLDASM', '').replace('.sldasm', '')
            output_path = os.path.join(
                os.path.expanduser('~'), 'Documents',
                f'Commande_Fournisseur_{doc_name}_{timestamp}.csv'
            )

        try:
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')

                # En-tete
                writer.writerow([
                    'Fournisseur', 'Reference', 'Designation',
                    'Quantite', 'Prix Unitaire HT', 'Prix Total HT'
                ])

                # Donnees
                total_general = 0
                current_supplier = None

                for order in sorted_orders:
                    # Separateur fournisseur
                    if group_by_supplier and order['fournisseur'] != current_supplier:
                        if current_supplier is not None:
                            writer.writerow([])  # Ligne vide entre fournisseurs
                        current_supplier = order['fournisseur']

                    writer.writerow([
                        order['fournisseur'],
                        order['reference'],
                        order['designation'],
                        order['quantite'],
                        f"{order['prix_unitaire']:.2f}",
                        f"{order['prix_total']:.2f}",
                    ])
                    total_general += order['prix_total']

                # Total general
                writer.writerow([])
                writer.writerow(['', '', 'TOTAL GENERAL', '', '', f"{total_general:.2f}"])

            self._add_log("INFO", f"Commande fournisseur generee: {output_path}")
            self._add_log("INFO", f"Total: {len(sorted_orders)} references, {total_general:.2f} EUR HT")
            return output_path

        except Exception as e:
            self._add_log("ERREUR", f"Erreur generation commande: {str(e)}")
            return ""

    def _enrich_from_db(self, components: List[Dict]) -> List[Dict]:
        """
        Enrichit les composants avec les donnees de la BDD.

        Pour chaque composant ayant un code, recherche dans catalogue.db
        et complete les informations manquantes (fournisseur, prix, etc.)
        """
        if self.db is None:
            return components

        enriched = []
        for comp in components:
            comp_copy = dict(comp)
            code = comp.get('code', '').strip()

            if code:
                prods = self.db.search_produits(terme=code, actif_only=True, limit=5)
                for prod in prods:
                    if prod.get('reference', '').strip().upper() == code.strip().upper():
                        # Enrichir avec les donnees BDD
                        if not comp_copy.get('supplier'):
                            comp_copy['supplier'] = prod.get('fournisseur', '')
                        if comp_copy.get('cost', 0) == 0:
                            comp_copy['cost'] = prod.get('prix_achat', 0)
                        comp_copy['db_designation'] = prod.get('designation', '')
                        comp_copy['db_id'] = prod.get('id')
                        break

            enriched.append(comp_copy)

        return enriched

    # =================================================================
    # MODE HORS-LIGNE (sans SolidWorks)
    # =================================================================

    def import_from_report_csv(self, csv_path: str) -> List[Dict]:
        """
        Importe les quincailleries depuis un CSV genere par le Report SWOOD.

        Methode alternative quand SolidWorks n'est pas disponible.
        Le Report SWOOD peut generer un CSV contenant les colonnes:
        Code, Supplier, Supplier_Reference, Cost, FOURNISSEUR, Quantity...

        Args:
            csv_path: Chemin du fichier CSV du Report SWOOD

        Returns:
            Liste de composants au meme format que traverse_assembly()
        """
        components = []

        if not os.path.exists(csv_path):
            self._add_log("ERREUR", f"Fichier non trouve: {csv_path}")
            return components

        try:
            # Detecter le delimiteur
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                first_line = f.readline()
                delimiter = ';' if ';' in first_line else ('\t' if '\t' in first_line else ',')

            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=delimiter)

                for row in reader:
                    # Mapper les colonnes du CSV vers notre format interne
                    comp = {
                        'name': row.get('Name', row.get('NOM', '')),
                        'path': '',
                        'is_hardware': True,
                        'swood_type': 'HARDWARE',
                        'depth': 0,
                        'properties': dict(row),
                        'code': row.get('Code', row.get('TO_Q_CODE', row.get('REFERENCE', ''))),
                        'supplier': row.get('Supplier', row.get('TO_Q_F', row.get('FOURNISSEUR', ''))),
                        'supplier_reference': row.get('Supplier_Reference', row.get('TO_Q_R', '')),
                        'cost': self._parse_float(row.get('Cost', row.get('TO_Q_UC', '0'))),
                        'description': row.get('Description', row.get('DESIGNATION', '')),
                        'finish': row.get('Finish', row.get('FINITION', '')),
                        'quantity': int(self._parse_float(row.get('Quantity', row.get('QTY', '1')))),
                    }
                    components.append(comp)

            self._add_log("INFO", f"Import CSV: {len(components)} composant(s) depuis {csv_path}")
            return components

        except Exception as e:
            self._add_log("ERREUR", f"Erreur import CSV: {str(e)}")
            return components

    def export_db_for_swood(self, output_path: str = None,
                            categorie: str = DEFAULT_HARDWARE_CATEGORY,
                            format_type: str = 'csv') -> str:
        """
        Exporte les produits depuis catalogue.db dans un format compatible SWOOD.

        Ce fichier peut ensuite etre utilise pour alimenter les proprietes
        personnalisees SolidWorks via une macro VBA ou le Report SWOOD.

        Args:
            output_path: Chemin de sortie (auto-genere si None)
            categorie: Categorie a exporter (defaut: QUINCAILLERIE SWOOD)
            format_type: 'csv' ou 'json'

        Returns:
            Chemin du fichier genere
        """
        if self.db is None:
            self._add_log("ERREUR", "Aucune base de donnees connectee")
            return ""

        # Recuperer les produits
        produits = self.db.search_produits(categorie=categorie, actif_only=True, limit=0)

        if not produits:
            self._add_log("AVERTISSEMENT", f"Aucun produit dans la categorie '{categorie}'")
            return ""

        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            ext = 'json' if format_type == 'json' else 'csv'
            output_path = os.path.join(
                os.path.expanduser('~'), 'Documents',
                f'Export_SWOOD_{timestamp}.{ext}'
            )

        try:
            if format_type == 'json':
                # Export JSON (utilisable par macro VBA ou Python)
                export_data = []
                for p in produits:
                    export_data.append({
                        'Code': p.get('reference', ''),
                        'Supplier': p.get('fournisseur', ''),
                        'Supplier_Reference': p.get('reference', ''),
                        'Cost': p.get('prix_achat', 0),
                        'FOURNISSEUR': p.get('fournisseur', ''),
                        'DESCRIPTION': p.get('designation', ''),
                        # Champs supplementaires
                        'Marque': p.get('marque', ''),
                        'Categorie': p.get('categorie', ''),
                        'Sous_Categorie': p.get('sous_categorie', ''),
                    })

                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)

            else:
                # Export CSV (delimiter ;, compatible SWOOD Report)
                with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f, delimiter=';')

                    writer.writerow([
                        'Code', 'Supplier', 'Supplier_Reference', 'Cost',
                        'FOURNISSEUR', 'DESCRIPTION', 'Marque',
                        'Categorie', 'Sous_Categorie'
                    ])

                    for p in produits:
                        writer.writerow([
                            p.get('reference', ''),
                            p.get('fournisseur', ''),
                            p.get('reference', ''),
                            p.get('prix_achat', 0),
                            p.get('fournisseur', ''),
                            p.get('designation', ''),
                            p.get('marque', ''),
                            p.get('categorie', ''),
                            p.get('sous_categorie', ''),
                        ])

            self._add_log("INFO", f"Export genere: {output_path} ({len(produits)} produits)")
            return output_path

        except Exception as e:
            self._add_log("ERREUR", f"Erreur export: {str(e)}")
            return ""

    # =================================================================
    # UTILITAIRES
    # =================================================================

    def _parse_float(self, value: str) -> float:
        """Convertit une chaine en float (gestion virgule et point)."""
        if not value:
            return 0.0
        try:
            return float(str(value).replace(',', '.').strip())
        except (ValueError, TypeError):
            return 0.0

    def _add_log(self, level: str, message: str):
        """Ajoute une entree au journal."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        entry = f"[{timestamp}] [{level}] {message}"
        self._log.append(entry)

        # Aussi logger via le module logging
        if level == "ERREUR":
            logger.error(message)
        elif level == "AVERTISSEMENT":
            logger.warning(message)
        else:
            logger.info(message)

    def get_log(self) -> List[str]:
        """Retourne le journal des operations."""
        return list(self._log)

    def clear_log(self):
        """Vide le journal."""
        self._log.clear()

    def get_status(self) -> Dict[str, Any]:
        """
        Retourne l'etat actuel du bridge.

        Returns:
            Dictionnaire avec les informations d'etat
        """
        return {
            'connected': self.connected,
            'active_document': self.get_active_document(),
            'database': self.db.db_path if self.db else None,
            'log_entries': len(self._log),
        }


# =====================================================================
# FONCTIONS UTILITAIRES AUTONOMES
# =====================================================================

def quick_scan_assembly(db_path: str = None) -> Dict:
    """
    Scan rapide : connecte a SolidWorks, lit l'assemblage, retourne un resume.

    Usage en une ligne depuis un terminal :
        python -c "from sw_bridge import quick_scan_assembly; print(quick_scan_assembly())"

    Args:
        db_path: Chemin vers catalogue.db (optionnel)

    Returns:
        Resume avec composants, correspondances BDD, statistiques
    """
    from database import Database

    db = Database(db_path) if db_path else Database()
    bridge = SolidWorksBridge(database=db)

    if not bridge.connect_solidworks():
        return {'error': 'Impossible de se connecter a SolidWorks', 'log': bridge.get_log()}

    components = bridge.traverse_assembly(include_hardware_only=True)

    # Verifier les correspondances BDD
    found_in_db = 0
    not_in_db = []

    for comp in components:
        code = comp.get('code', '').strip()
        if code:
            prods = db.search_produits(terme=code, actif_only=True, limit=5)
            match = any(p.get('reference', '').strip().upper() == code.upper() for p in prods)
            if match:
                found_in_db += 1
            else:
                not_in_db.append(code)

    return {
        'document': bridge.get_active_document(),
        'total_hardware': len(components),
        'found_in_db': found_in_db,
        'missing_in_db': not_in_db,
        'components': components,
        'log': bridge.get_log(),
    }


def sync_from_csv(csv_path: str, db_path: str = None,
                  create_missing: bool = True) -> Dict[str, int]:
    """
    Synchronise un CSV de Report SWOOD vers catalogue.db (mode sans SolidWorks).

    Usage:
        python sw_bridge.py sync report_export.csv

    Args:
        csv_path: Chemin du CSV genere par le Report SWOOD
        db_path: Chemin vers catalogue.db (optionnel)
        create_missing: Creer les produits absents

    Returns:
        Statistiques de synchronisation
    """
    from database import Database

    db = Database(db_path) if db_path else Database()
    bridge = SolidWorksBridge(database=db)

    components = bridge.import_from_report_csv(csv_path)
    stats = bridge.sync_hardware_to_db(components, create_if_missing=create_missing)

    # Afficher le log
    for entry in bridge.get_log():
        print(entry)

    return stats


# =====================================================================
# POINT D'ENTREE CLI
# =====================================================================

if __name__ == '__main__':
    """
    Usage en ligne de commande:

        python sw_bridge.py scan              # Scan l'assemblage SW actif
        python sw_bridge.py sync fichier.csv  # Sync depuis CSV Report SWOOD
        python sw_bridge.py export            # Export BDD vers format SWOOD
        python sw_bridge.py status            # Affiche l'etat du bridge
    """

    if len(sys.argv) < 2:
        print("Usage: python sw_bridge.py <commande> [arguments]")
        print("")
        print("Commandes disponibles:")
        print("  scan              Scanne l'assemblage SolidWorks actif")
        print("  sync <fichier>    Synchronise un CSV Report SWOOD vers la BDD")
        print("  export [csv|json] Exporte la BDD vers un format SWOOD")
        print("  status            Affiche l'etat de connexion")
        print("  order             Genere une commande fournisseur depuis l'assemblage")
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == 'scan':
        result = quick_scan_assembly()
        if 'error' in result:
            print(f"ERREUR: {result['error']}")
        else:
            print(f"\nDocument: {result['document']}")
            print(f"Quincailleries: {result['total_hardware']}")
            print(f"Trouvees dans BDD: {result['found_in_db']}")
            if result['missing_in_db']:
                print(f"Absentes de la BDD ({len(result['missing_in_db'])}):")
                for code in result['missing_in_db']:
                    print(f"  - {code}")

    elif command == 'sync':
        if len(sys.argv) < 3:
            print("Usage: python sw_bridge.py sync <fichier_csv>")
            sys.exit(1)
        csv_file = sys.argv[2]
        stats = sync_from_csv(csv_file)
        print(f"\nResultat: {stats}")

    elif command == 'export':
        from database import Database
        fmt = sys.argv[2] if len(sys.argv) > 2 else 'csv'
        db = Database()
        bridge = SolidWorksBridge(database=db)
        path = bridge.export_db_for_swood(format_type=fmt)
        if path:
            print(f"Fichier genere: {path}")
        for entry in bridge.get_log():
            print(entry)

    elif command == 'status':
        from database import Database
        db = Database()
        bridge = SolidWorksBridge(database=db)
        connected = bridge.connect_solidworks()
        status = bridge.get_status()
        print(f"\nEtat du bridge SolidWorks <-> DestriChiffrage")
        print(f"{'='*50}")
        print(f"SolidWorks connecte: {'OUI' if status['connected'] else 'NON'}")
        print(f"Document actif: {status['active_document'] or 'Aucun'}")
        print(f"Base de donnees: {status['database']}")
        print(f"Produits en BDD: {db.count_produits()}")
        print(f"Quincailleries: {db.count_produits(DEFAULT_HARDWARE_CATEGORY)}")

    elif command == 'order':
        from database import Database
        db = Database()
        bridge = SolidWorksBridge(database=db)
        if bridge.connect_solidworks():
            path = bridge.generate_supplier_order()
            if path:
                print(f"Commande generee: {path}")
        for entry in bridge.get_log():
            print(entry)

    else:
        print(f"Commande inconnue: {command}")
        print("Utilisez: scan, sync, export, status, order")
