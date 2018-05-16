#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import *
from modeles import modeleResanet
from technique import datesResanet


app = Flask( __name__ )
app.secret_key = 'resanet'


@app.route( '/' , methods = [ 'GET' ] )
def index() :
	return render_template( 'vueAccueil.html' )

@app.route( '/usager/session/choisir' , methods = [ 'GET' ] )
def choisirSessionUsager() :
	return render_template( 'vueConnexionUsager.html' , carteBloquee = False , echecConnexion = False , saisieIncomplete = False )

@app.route( '/usager/seConnecter' , methods = [ 'POST' ] )
def seConnecterUsager() :
	numeroCarte = request.form[ 'numeroCarte' ]
	mdp = request.form[ 'mdp' ]

	if numeroCarte != '' and mdp != '' :
		usager = modeleResanet.seConnecterUsager( numeroCarte , mdp )
		if len(usager) != 0 :
			if usager[ 'activee' ] == True :
				session[ 'numeroCarte' ] = usager[ 'numeroCarte' ]
				session[ 'nom' ] = usager[ 'nom' ]
				session[ 'prenom' ] = usager[ 'prenom' ]
				session[ 'mdp' ] = mdp
				
				return redirect( '/usager/reservations/lister' )
				
			else :
				return render_template('vueConnexionUsager.html', carteBloquee = True , echecConnexion = False , saisieIncomplete = False )
		else :
			return render_template('vueConnexionUsager.html', carteBloquee = False , echecConnexion = True , saisieIncomplete = False )
	else :
		return render_template('vueConnexionUsager.html', carteBloquee = False , echecConnexion = False , saisieIncomplete = True)


@app.route( '/usager/seDeconnecter' , methods = [ 'GET' ] )
def seDeconnecterUsager() :
	session.pop( 'numeroCarte' , None )
	session.pop( 'nom' , None )
	session.pop( 'prenom' , None )
	return redirect( '/' )


@app.route( '/usager/reservations/lister' , methods = [ 'GET' ] )
def listerReservations() :
	tarifRepas = modeleResanet.getTarifRepas( session[ 'numeroCarte' ] )
	
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	
	solde = '%.2f' % ( soldeCarte , )

	aujourdhui = datesResanet.getDateAujourdhuiISO()

	datesPeriodeISO = datesResanet.getDatesPeriodeCouranteISO()
	
	datesResas = modeleResanet.getReservationsCarte( session[ 'numeroCarte' ] , datesPeriodeISO[ 0 ] , datesPeriodeISO[ -1 ] )
	
	dates = []
	
	dateFerie = modeleResanet.getFerie(datesPeriodeISO[0])
	
	for uneDateISO in datesPeriodeISO :
		uneDate = {}
		uneDate[ 'iso' ] = uneDateISO
		uneDate[ 'fr' ] = datesResanet.convertirDateISOversFR( uneDateISO )
			
		if uneDateISO <= aujourdhui:
			uneDate[ 'verrouillee' ] = True
		else :
			uneDate[ 'verrouillee' ] = False
				
		
	
		if uneDateISO in datesResas :
			uneDate[ 'reservee' ] = True
		else :
			uneDate[ 'reservee' ] = False
		
		if soldeCarte < tarifRepas and uneDate[ 'reservee' ] == False :
			uneDate[ 'verrouillee' ] = True
			
		if uneDateISO in dateFerie :
			uneDate[ 'verrouillee' ] = True
		
		dates.append( uneDate )
		
	
	if soldeCarte < tarifRepas :
		soldeInsuffisant = True
	else :
		soldeInsuffisant = False
		
	jour = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Lundi","Mardi","Mercredi","Jeudi","Vendredi"]
		
	
	return render_template( 'vueListeReservations.html' , laSession = session , leSolde = solde , lesDates = dates , soldeInsuffisant = soldeInsuffisant , jour = jour)

	
@app.route( '/usager/reservations/annuler/<dateISO>' , methods = [ 'GET' ] )
def annulerReservation( dateISO ) :
	modeleResanet.annulerReservation( session[ 'numeroCarte' ] , dateISO )
	modeleResanet.crediterSolde( session[ 'numeroCarte' ] )
	return redirect( '/usager/reservations/lister' )
	
@app.route( '/usager/reservations/enregistrer/<dateISO>' , methods = [ 'GET' ] )
def enregistrerReservation( dateISO ) :
	modeleResanet.enregistrerReservation( session[ 'numeroCarte' ] , dateISO )
	modeleResanet.debiterSolde( session[ 'numeroCarte' ] )
	return redirect( '/usager/reservations/lister' )

@app.route( '/usager/mdp/modification/choisir' , methods = [ 'GET' ] )
def choisirModifierMdpUsager() :
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	solde = '%.2f' % ( soldeCarte , )
	
	return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = '' )

@app.route( '/usager/mdp/modification/appliquer' , methods = [ 'POST' ] )
def modifierMdpUsager() :
	ancienMdp = request.form[ 'ancienMDP' ]
	nouveauMdp = request.form[ 'nouveauMDP' ]
	
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	solde = '%.2f' % ( soldeCarte , )
	
	if ancienMdp != session[ 'mdp' ] or nouveauMdp == '' :
		return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = 'Nok' )
		
	else :
		modeleResanet.modifierMdpUsager( session[ 'numeroCarte' ] , nouveauMdp )
		session[ 'mdp' ] = nouveauMdp
		return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = 'Ok' )


@app.route( '/gestionnaire/session/choisir' , methods = [ 'GET' ] )
def choisirSessionGestionnaire() :
	return render_template( 'vueConnexionGestionnaire.html' )

@app.route( '/gestionnaire/seConnecter' , methods = [ 'POST' ] )
def seConnecterGestionnaire() :
	login = request.form[ 'login' ]
	mdp = request.form[ 'mdp' ]

	if login != '' and mdp != '' :
		gestionnaire = modeleResanet.seConnecterGestionnaire( login , mdp )
		if len(gestionnaire) != 0 :
			session[ 'login' ] = gestionnaire[ 'login' ]
			session[ 'nom' ] = gestionnaire[ 'nom' ]
			session[ 'prenom' ] = gestionnaire[ 'prenom' ]
			session[ 'mdp' ] = mdp
				
			return redirect("/gestionnaire/avecCarte")
		else :
			return render_template('vueConnexionGestionnaire.html', echecConnexion = True , saisieIncomplete = False )
	else :
		return render_template('vueConnexionGestionnaire.html', echecConnexion = False , saisieIncomplete = True)

@app.route( '/gestionnaire/seDeconnecter' , methods = [ 'GET' ] )
def seDeconnecterGestionnaire() :
	session.pop( 'login' , None )
	session.pop( 'nom' , None )
	session.pop( 'prenom' , None )
	return redirect( '/' )

@app.route( '/gestionnaire/sansCarte' , methods = [ 'GET' ] )
def listerPersoSansCarte() :
	personnel = modeleResanet.getPersonnelsSansCarte()
	rangePersonnel = len(personnel)
	nom = []
	prenom = []
	matricule = []
	nomService = []
	
	for unNom in personnel :
		nom.append(unNom['nom'])
		
	for unPrenom in personnel :
		prenom.append(unPrenom['prenom'])
		
	for uneMatricule in personnel :
		matricule.append(str(uneMatricule['matricule']))
		
	for unService in personnel :
		nomService.append(unService['nomService'])
	
	return render_template('vuePersonnelSansCarte.html', leNom = nom, lePrenom = prenom, laMatricule = matricule, leService = nomService, rangePerso = rangePersonnel)


@app.route( '/gestionnaire/avecCarte' , methods = [ 'GET' ] )
def listerPersoAvecCarte() :
	personnel = modeleResanet.getPersonnelsAvecCarte()
	rangePersonnel = len(personnel)
	nom = []
	prenom = []
	matricule = []
	nomService = []
	solde = []
	activee = []
	noCarte = []
	
	for unNom in personnel :
		nom.append(unNom['nom'])
		
	for unPrenom in personnel :
		prenom.append(unPrenom['prenom'])
		
	for uneMatricule in personnel :
		matricule.append(str(uneMatricule['matricule']))
		
	for unService in personnel :
		nomService.append(unService['nomService'])
		
	for unSolde in personnel :
		solde.append(unSolde['solde'])
	
	for unActivee in personnel :
		activee.append(unActivee['activee'])
	
	for unNoCarte in personnel :
		noCarte.append(unNoCarte['numeroCarte'])
	
	return render_template('vuePersonnelAvecCarte.html', leNom = nom, lePrenom = prenom, laMatricule = matricule, leService = nomService, rangePerso = rangePersonnel, leSolde = solde, actif = activee, leNoCarte = noCarte)

@app.route( '/gestionnaire/avecCarte/bloquer' , methods = [ 'POST' ] )
def bloquerCarte() :
	noCarte = request.form['numeroCarte']
	modeleResanet.bloquerCarte(noCarte)
	return redirect("/gestionnaire/avecCarte")


@app.route( '/gestionnaire/avecCarte/activer' , methods = [ 'POST' ] )
def activerCarte() :
	noCarte = request.form['numeroCarte']
	modeleResanet.activerCarte( noCarte )
	return redirect("/gestionnaire/avecCarte")

@app.route( '/gestionnaire/avecCarte/crediter' , methods = [ 'POST' ] )
def crediterCarte() :
	noCarte = request.form['numeroCarte']
	return render_template('vueCrediterCarte.html', leNoCarte = noCarte)
	
@app.route( '/gestionnaire/avecCarte/crediter/montant' , methods = [ 'POST' ] )
def montantCredite() :
	noCarte = request.form['numeroCarte']
	montant = request.form['credit']
	modeleResanet.crediterCarte(noCarte,montant)
	return redirect("/gestionnaire/avecCarte")
	
	
@app.route( '/gestionnaire/avecCarte/resetMdp' , methods = [ 'POST' ] )
def initCarte() :
	noCarte = request.form['numeroCarte']
	modeleResanet.reinitialiserMdp(noCarte)
	return redirect("/gestionnaire/avecCarte")
	
@app.route( '/gestionnaire/avecCarte/histo' , methods = [ 'POST' ] )
def getHisto() :
	noCarte = request.form['numeroCarte']
	historique = modeleResanet.getHistoriqueReservationsCarte(noCarte)
	rangeHistorique = len(historique)
	return render_template("vueHistorique.html", histo = historique, leNoCarte = noCarte, rangeHisto = rangeHistorique)
	
@app.route('/gestionnaire/sansCarte/creationCompte' , methods = [ 'POST' ] )
def creerCompte() :
	matricule = request.form['matricule']
	modeleResanet.creerCarte( matricule )
	return redirect("/gestionnaire/sansCarte")
	
@app.route('/gestionnaire/historique/pourCarte' , methods = [ 'GET' ])
def pourCarte() :
	personnel = modeleResanet.getPersonnelsAvecCarte()
	rangePersonnel = len(personnel)
	nom = []
	prenom = []
	noCarte = []
	nomService = []
	
	for unNom in personnel :
		nom.append(unNom['nom'])
		
	for unPrenom in personnel :
		prenom.append(unPrenom['prenom'])
		
	for uneNoCarte in personnel :
		noCarte.append(str(uneNoCarte['numeroCarte']))
		
	for unService in personnel :
		nomService.append(unService['nomService'])
	
	
	return render_template("vueHistoPourCarte.html", leNom = nom, lePrenom = prenom, leNoCarte = noCarte, leService = nomService, rangePerso = rangePersonnel)
	
@app.route('/gestionnaire/historique/pourDate' , methods = [ 'GET' ])
def pourDate() :
	personnel = modeleResanet.getPersonnelsAvecCarte()
	rangePersonnel = len(personnel)
	nom = []
	prenom = []
	noCarte = []
	nomService = []
	solde = []
	activee = []
	
	for unNom in personnel :
		nom.append(unNom['nom'])
		
	for unPrenom in personnel :
		prenom.append(unPrenom['prenom'])
		
	for unNoCarte in personnel :
		noCarte.append(str(unNoCarte['numeroCarte']))
		
	for unService in personnel :
		nomService.append(unService['nomService'])
	
	
	return render_template("vueHistoPourDate.html", leNom = nom, lePrenom = prenom, leNoCarte = noCarte, leService = nomService, rangePerso = rangePersonnel, leSolde = solde, actif = activee)

@app.route('/gestionnaire/historique/pourDate/laDate' , methods = [ 'POST' ])
def laDate() :
	date = request.form['laDate']
	listeDate = modeleResanet.getReservationsDate(date)
	nom = []
	prenom = []
	noCarte = []
	nomService = []
	
	for unNom in listeDate :
		nom.append(unNom['nom'])
		
	for unPrenom in listeDate :
		prenom.append(unPrenom['prenom'])
		
	for uneNoCarte in listeDate :
		noCarte.append(str(uneNoCarte['numeroCarte']))
		
	for unService in listeDate :
		nomService.append(unService['nomService'])
		
	rangeDate = len(nom)

	return render_template("vueHistoriqueDate.html", uneDate = date,rangeD = rangeDate, leNoCarte = noCarte, leNom = nom, lePrenom = prenom ,leService = nomService)
	

if __name__ == '__main__' :
	app.run( debug = True , host = '0.0.0.0' , port = 5000 )
