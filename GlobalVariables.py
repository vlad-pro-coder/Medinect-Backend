import re
import threading
from unidecode import unidecode

procentageReadySraper = {}
ResultsScraper = {}
threadLock = threading.Lock()
PerLettersTypoTolerance = 4 #per {value} characters it will accept a typo

def hasKeyWords(name,TrieWords):

    name = name.lower()#upper letters have no sens
    name = unidecode(name)#other langauges extra letters besides english ones get transformed their english equivalent
    words = re.findall(r"\b[a-zA-Z]+\b",name)#same regex rules like in entryPoint.py
    TakeCandidate = False

    for word in words:#for every word in the products title we make a verification
        #calculate the typo tolerance
        TypoTolerance = len(word) / PerLettersTypoTolerance
        if len(word) % PerLettersTypoTolerance != 0:
            TypoTolerance+=1
        #determine if the word is a match or no
        TakeCandidate = TakeCandidate or TrieWords.start_search_possible_matches(word,TypoTolerance)

    return TakeCandidate

#for the next 8 functions these are the we scarper rules and how the web scraper gets its items
#based on the site layout these function take the link of the product, link of the product's image and the name of the product
#the results are appended to a reference from an existing list of these results
def farm_tei_scraper(soup,_,ScrapedData,TrieWords):
        # This function can be customized to extract data as needed
        products = soup.findAll('div', class_='product-item')

        for product in products:
            aux1 = product.findAll('a', class_='item-title')
            if aux1 == []:
                continue
            aux2 = aux1[0].findAll('h4')
            if aux2 == []:
                continue
            name = aux2[0].text
            if hasKeyWords(name,TrieWords):
                data = {
                    'name':name,
                    'link':aux1[0]['href'],
                    'imagelink':product.findAll('a', class_='product-image-listing')[0].findAll('picture')[0].findAll('img')[0]['src']
                }
                #print(data)
                ScrapedData.append(data)

def drmax_scraper(soup,domain,ScrapedData,TrieWords):
    # This function can be customized to extract data as needed
    products = soup.findAll('li', class_='tile')

    for product in products:
        #print(product)
        aux = product.findAll('h3','tile__title')
        if aux == []:
            continue
        name = aux[0].text

        if hasKeyWords(name,TrieWords):
            data = {
                'name':name,
                'link':domain + product.findAll('div',class_='tile__image')[0].findAll('a')[0]['href'],
                'imagelink':domain + product.findAll('picture',class_='lazy-image')[0].findAll('img')[0]['src']
            }
            #print(data)
            ScrapedData.append(data)

def medicalsupermarket_scraper(soup,domain,ScrapedData,TrieWords):
    products = soup.findAll(class_='productListItemContent')

    for product in products:
        aux = product.findAll('div',class_='productListItemProductName')

        if aux == []:
            continue
        name = aux[0].text

        if hasKeyWords(name,TrieWords):
            data = {
                'name':name,
                'link':domain + product.findAll('div',class_="productListItemImage")[0].findAll('a')[0]['href'],
                'imagelink':product.findAll('div',class_="productListItemImage")[0].findAll('img')[0]['src']
            }
            #print(data)
            ScrapedData.append(data)

def chemistdirect_scraper(soup,domain,ScrapedData,TrieWords):
    products = soup.findAll('li',class_='cd-p-item')

    for product in products:
        
        aux = product.findAll('a',class_='cd-p-name')

        if aux == []:
            continue
        name = aux[0].text

        if hasKeyWords(name,TrieWords):
            data = {
                'name':name,
                'link':domain + aux[0]['href'],
                'imagelink':product.findAll('img',class_="cd-p-img")[0]['src']
            }
            #print(data)
            ScrapedData.append(data)

def francehealth_scraper(soup,_,ScrapedData,TrieWords):
    products = soup.findAll('article',class_='product-miniature')

    for product in products:
    
        aux = product.findAll(class_='product-name')[0].findAll('a')

        if aux == []:
            continue

        name = aux[0].text
        if hasKeyWords(name,TrieWords):
            data = {
                'name':name,
                'link':product.findAll('a',class_='product-cover-link')[0]['href'],
                'imagelink':product.select('link[itemprop="image"]')[0]['href'],
            }
            #print(data)
            ScrapedData.append(data)

def europharmas_scraper(soup,_,ScrapedData,TrieWords):
    products = soup.findAll('div',class_='product-miniature')

    for product in products:
    
        aux = product.findAll(class_='product-title')[0].findAll('a')

        if aux == []:
            continue

        name = aux[0].text
        if hasKeyWords(name,TrieWords):
            data = {
                'name':name,
                'link':aux[0]['href'],
                'imagelink':product.findAll('div',class_ = 'thumbnail-container')[0].find('img')['src'],
            }
            #print(data)
            ScrapedData.append(data)

def arzneiprivat_scraper(soup,_,ScrapedData,TrieWords):
    products = soup.findAll('article',class_='product-box')

    for product in products:
    
        aux = product.findAll('h1',class_='product-box__title')

        if aux == []:
            continue

        name = aux[0].text
        if hasKeyWords(name,TrieWords):
            data = {
                'name':name,
                'link':product.findAll('a',class_="pb-2 block")[0]['href'],
                'imagelink':product.findAll('figure',class_="product-box__image")[0].findAll('img')[0]['src'],
            }
            #print(data)
            ScrapedData.append(data)

def paulsmarteurope_scraper(soup,_,ScrapedData,TrieWords):
    productseven = soup.findAll('ul',class_='ProductList')[0].findAll('li',class_='Even')
    productodd = soup.findAll('ul',class_='ProductList')[0].findAll('li',class_='Odd')

    products = productseven + productodd

    for product in products:
    
        aux = product.findAll('a',class_='pname')

        if aux == []:
            continue

        name = aux[0].text
        if hasKeyWords(name,TrieWords):
            data = {
                'name':name,
                'link':aux[0]['href'],
                'imagelink':product.find('a').find('img')['src'],
            }
            #print(data)
            ScrapedData.append(data)

#the links we scrape based on nationality
scrapeSites = {
    'ron':[
        'https://comenzi.farmaciatei.ro/medicamente-otc',
        'https://comenzi.farmaciatei.ro/medicamente-cu-reteta',
        'https://comenzi.farmaciatei.ro/dispozitive-medicale',
        'https://comenzi.farmaciatei.ro/vitamine-si-suplimente',
        'https://comenzi.farmaciatei.ro/dermato-cosmetice',
        'https://comenzi.farmaciatei.ro/cosmetice-premium',
        'https://comenzi.farmaciatei.ro/ingrijire-personala',
        'https://comenzi.farmaciatei.ro/dieta-si-wellness',
        'https://comenzi.farmaciatei.ro/viata-sexuala',
        'https://comenzi.farmaciatei.ro/vet',

        'https://www.drmax.ro/marca-proprie',
        'https://www.drmax.ro/medicamente-fara-reteta',
        'https://www.drmax.ro/suplimente-alimentare',
        'https://www.drmax.ro/mama-si-copilul',
        'https://www.drmax.ro/frumusete-si-ingrijire',
        'https://www.drmax.ro/frumusete-si-ingrijire/dermatocosmetice',
        'https://www.drmax.ro/dieta-si-nutritie',
        'https://www.drmax.ro/subiecte-tabu',
        'https://www.drmax.ro/tehnico-medicale',
        'https://www.drmax.ro/cuplu-si-sex',
        'https://www.drmax.ro/eco',
        'https://www.drmax.ro/frumusete-si-ingrijire/machiaj'
    ],
    'eng':[
        'https://www.medical-supermarket.com/Products/1491/Infection-Control',
        'https://www.medical-supermarket.com/Products/3105/Dressings-Wound-Care',
        'https://www.medical-supermarket.com/Products/1504/Gynaecology-and-Midwifery',
        'https://www.medical-supermarket.com/Products/1495/Diagnostics',
        'https://www.medical-supermarket.com/Products/1481/Minor-Surgery',
        'https://www.medical-supermarket.com/Products/1559/Respiratory',
        'https://www.medical-supermarket.com/SUSI/Single-Use-Medical-Instruments',
        'https://www.medical-supermarket.com/Products/3107/Sharps-Cannula',
        'https://www.medical-supermarket.com/Products/1672/Infection-Control-Clothing',
        'https://www.medical-supermarket.com/Products/1866/Patient-Care',
        'https://www.medical-supermarket.com/Products/2221/Paper-Towels-and-Toilet-Tissues',
        'https://www.medical-supermarket.com/Products/1551/Pharmaceuticals',
        'https://www.medical-supermarket.com/Products/2152/Cleaning-Supplies-Equipment',
        'https://www.medical-supermarket.com/Products/3045/Ready-to-Use-Products',
        'https://www.medical-supermarket.com/Products/2975/Linen-and-Laundry-Management',
        'https://www.medical-supermarket.com/Products/2205/Facilities-Management',
        'https://www.medical-supermarket.com/Products/2221/Paper-Towels-and-Toilet-Tissues',
        'https://www.medical-supermarket.com/Products/3044/Cleaning-Chemicals',
        'https://www.medical-supermarket.com/Products/3046/Concentrate-Products',
        'https://www.medical-supermarket.com/Products/2160/Cleaning-Equipment',

        'https://www.chemistdirect.co.uk/'
    ],
    'fra':[
        'https://www.france-health.com/fr/940-aiguille-canule-roller',
        'https://www.france-health.com/fr/1143-fils-tenseurs-',
        'https://www.france-health.com/fr/463-dermatologie-marques-',
        'https://www.france-health.com/fr/67-dermatologie-anti-age',
        'https://www.france-health.com/fr/1612-nutricosmetique-beaute',
        'https://www.france-health.com/fr/1117-zones-de-traitement',
        'https://www.france-health.com/fr/1545-aliaxin-ibsa-derma',
        'https://www.france-health.com/fr/1030-aquashine-caregen',
        'https://www.france-health.com/fr/479-belotero-merz-pharmaceuticals',
        'https://www.france-health.com/fr/1611-countourel-croma',
        'https://www.france-health.com/fr/953-cytocare-revitacare',
        'https://www.france-health.com/fr/1468-definisse-relife-menarini-group',
        'https://www.france-health.com/fr/1186-dermica-solutions-cosmetics',
        'https://www.france-health.com/fr/997-desirial',
        'https://www.france-health.com/fr/1561-dp-dermaceuticals-dermapenworld',
        'https://www.france-health.com/fr/1578-dr-cyj-hair-filler',
        'https://www.france-health.com/fr/583-ellanse-sinclair',
        'https://www.france-health.com/fr/1326-fillmed',
        'https://www.france-health.com/fr/1553-harmonyca-allergan',
        'https://www.france-health.com/fr/1196-hyacorp-bioscience',
        'https://www.france-health.com/fr/1274-hyamira',
        'https://www.france-health.com/fr/1118-inex-dispoderm-kipic',
        'https://www.france-health.com/fr/1555-infini-fillers-',
        'https://www.france-health.com/fr/1172-innoaesthetics',
        'https://www.france-health.com/fr/1016-jalupro',
        'https://www.france-health.com/fr/470-juvederm-allergan',
        'https://www.france-health.com/fr/1524-luna-q-plcl',
        'https://www.france-health.com/fr/1502-lanluma-sinclair',
        'https://www.france-health.com/fr/1520-maili-sinclair',
        'https://www.france-health.com/fr/1214-me-line-innoaesthetics',
        'https://www.france-health.com/fr/644-mesoline-pluryal',
        'https://www.france-health.com/fr/912-neauvia-matexlab',
        'https://www.france-health.com/fr/522-perfectha-sinclair',
        'https://www.france-health.com/fr/1554-philart-croma',
        'https://www.france-health.com/fr/634-pluryal-md-skin-solutions',
        'https://www.france-health.com/fr/1577-prostrolane-caregen',
        'https://www.france-health.com/fr/1542-profhilo-ibsa',
        'https://www.france-health.com/fr/527-radiesse-merz',
        'https://www.france-health.com/fr/464-restylane-galderma',
        'https://www.france-health.com/fr/1372-revanesse-prollenium-medical-',
        'https://www.france-health.com/fr/1394-revolax',
        'https://www.france-health.com/fr/514-saypha-princess-croma',
        'https://www.france-health.com/fr/582-sculptra-galderma',
        'https://www.france-health.com/fr/1600-silhouette-soft-sinclair',
        'https://www.france-health.com/fr/939-softfil',
        'https://www.france-health.com/fr/528-stylage-vivacy',
        'https://www.france-health.com/fr/1540-suisselle-cellbooster',
        'https://www.france-health.com/fr/469-teosyal-teoxane',
        'https://www.france-health.com/fr/1119-tsk-steriglide-canules-aiguilles',
        'https://www.france-health.com/fr/1551-viscoderm-ibsa-derma',

        'https://euro-pharmas.com/fr/7-hygiene-cosmetics',
        'https://euro-pharmas.com/fr/171-health-care',
        'https://euro-pharmas.com/fr/25-aromatherapy-herbalist',
        'https://euro-pharmas.com/fr/55-vitamins-and-supplements',
        'https://euro-pharmas.com/fr/211-baby-care',
        'https://euro-pharmas.com/fr/189-gastroenterology-medication',
        'https://euro-pharmas.com/fr/8-face',
        'https://euro-pharmas.com/fr/22-body',
        'https://euro-pharmas.com/fr/20-hair',
        'https://euro-pharmas.com/fr/19-sunscreen',
        'https://euro-pharmas.com/fr/129-make-up',
        'https://euro-pharmas.com/fr/105-perfumery',
        'https://euro-pharmas.com/fr/172-insects-and-bites',
        'https://euro-pharmas.com/fr/150-covid-19',
        'https://euro-pharmas.com/fr/205-nasal-spray',
        'https://euro-pharmas.com/fr/240-sexuality',
        'https://euro-pharmas.com/fr/227-damaged-skin',
        'https://euro-pharmas.com/fr/133-autotest',
        'https://euro-pharmas.com/fr/27-buy-essential-oils',
        'https://euro-pharmas.com/fr/78-herbalist-online',
        'https://euro-pharmas.com/fr/89-tonus-energy',
        'https://euro-pharmas.com/fr/90-probiotics-immune-system',
        'https://euro-pharmas.com/fr/223-probiotics-pharmacy',
        'https://euro-pharmas.com/fr/93-natural-sleep-aid-supplement',
        'https://euro-pharmas.com/fr/125-memory-supplement',
        'https://euro-pharmas.com/fr/87-treatment-medication-hevy-legs-hemorrhoids',
        'https://euro-pharmas.com/fr/122-medicine-motion-sickness',
        'https://euro-pharmas.com/fr/121-eye-sphere',
        'https://euro-pharmas.com/fr/92-smoking-cessation',
        'https://euro-pharmas.com/fr/142-glycemia',
        'https://euro-pharmas.com/fr/110-cholesterol',
        'https://euro-pharmas.com/fr/119-supplement-weight-loss',
        'https://euro-pharmas.com/fr/117-effective-detox-product',
        'https://euro-pharmas.com/fr/86-urinary-comfort',
        'https://euro-pharmas.com/fr/94-mobility',
        'https://euro-pharmas.com/fr/91-natural-remedies-against-cold',
        'https://euro-pharmas.com/fr/118-supplement-menopause',
        'https://euro-pharmas.com/fr/88-natural-supplement-for-digestion',
        'https://euro-pharmas.com/fr/208-supplements-baby-kids',
        'https://euro-pharmas.com/fr/211-baby-care',
        'https://euro-pharmas.com/fr/209-pregnancy',
        'https://euro-pharmas.com/fr/215-bath-skin-hair',
        'https://euro-pharmas.com/fr/216-oral-hygiene',
        'https://euro-pharmas.com/fr/43-ent-medicine-online-pharmacy',
        'https://euro-pharmas.com/fr/189-gastroenterology-medication',
        'https://euro-pharmas.com/fr/42-pain-and-fever',
        'https://euro-pharmas.com/fr/198-first-aid-medicine',
        'https://euro-pharmas.com/fr/39-online-medicine-for-venous-circulation',
        'https://euro-pharmas.com/fr/134-gynecology',
        'https://euro-pharmas.com/fr/202-ophthalmology',
        'https://euro-pharmas.com/fr/220-urinary-troubles-medicines',
        'https://euro-pharmas.com/fr/170-dermatology',
        'https://euro-pharmas.com/fr/44-smoking-cessation',
        
    ],
    'deu':[
        'https://www.arzneiprivat.de/category/arzneimittel.10.html',
        'https://www.arzneiprivat.de/category/hautpflege.16.html',
        'https://www.arzneiprivat.de/category/medizinprodukte.280.html',
        'https://www.arzneiprivat.de/category/abfuehrmittel.62.html',
        'https://www.arzneiprivat.de/category/allergie-heuschnupfen.79.html',
        'https://www.arzneiprivat.de/category/alles-fuer-die-frau.43.html',
        'https://www.arzneiprivat.de/category/liebe-potenz.133.html',
        'https://www.arzneiprivat.de/category/schmerzmittel.285.html',
        'https://www.arzneiprivat.de/category/augen-nase-ohren.11.html',
        'https://www.arzneiprivat.de/category/beruhigung-schlaf.65.html',
        'https://www.arzneiprivat.de/category/venenmittel.52.html',
        'https://www.arzneiprivat.de/category/haare-haut-schleimhaut.118.html',
        'https://www.arzneiprivat.de/category/herz-kreislauf.36.html',
        'https://www.arzneiprivat.de/category/hals-mund-rachen.32.html',
        'https://www.arzneiprivat.de/category/erkaeltung-abwehr.15.html',
        'https://www.arzneiprivat.de/category/staerkung-konzentration.24.html',
        'https://www.arzneiprivat.de/category/familie-baby.85.html',
        'https://www.arzneiprivat.de/category/infektion-wundbehandlung.37.html',
        'https://www.arzneiprivat.de/category/niere-blase-prostata.33.html',
        'https://www.arzneiprivat.de/category/magen-darm-galle.19.html',
        'https://www.arzneiprivat.de/category/raucherentwoehnung.82.html',
        'https://www.arzneiprivat.de/category/rheuma-muskelschmerz.38.html',
        
        'https://www.paulsmarteurope.com/acid-reflux-digestive/',
        'https://www.paulsmarteurope.com/pet-care/',
        'https://www.paulsmarteurope.com/stress-irritation/',
        'https://www.paulsmarteurope.com/allergies-hay-fever/',
        'https://www.paulsmarteurope.com/anxiety-nerves/',
        'https://www.paulsmarteurope.com/baby-child/',
        'https://www.paulsmarteurope.com/bandages-aids/',
        'https://www.paulsmarteurope.com/beauty/',
        'https://www.paulsmarteurope.com/categories/Bladder%2C-Kidney%2C-Prostate/',
        'https://www.paulsmarteurope.com/categories/Blood-Sugar-Diabetic-support/',
        'https://www.paulsmarteurope.com/brain-mind-mood/',
    ]
}

#the rules we use based on nationality
scrapeRules = {
    'ron':{
        'https://www.drmax.ro':drmax_scraper,
        'https://comenzi.farmaciatei.ro':farm_tei_scraper,
    },
    'eng':{
        'https://www.medical-supermarket.com':medicalsupermarket_scraper,
        'https://www.chemistdirect.co.uk':chemistdirect_scraper,
    },
    'fra':{
        'https://www.france-health.com':francehealth_scraper,
        'https://euro-pharmas.com':europharmas_scraper,
    },
    'deu':{
        'https://www.arzneiprivat.de':arzneiprivat_scraper,
        'https://www.paulsmarteurope.com':paulsmarteurope_scraper,
    }
}