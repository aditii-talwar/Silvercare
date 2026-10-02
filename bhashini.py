"""
Bhashini Multilingual AI Assistant Module
Powered by MeitY Bhashini / ULCA (National Language Translation Mission)
Supports: Hindi, English, Bengali, Tamil, Telugu, Marathi, Gujarati
"""

import os
import json
import urllib.request
import urllib.error

# Bhashini Dhruva / ULCA API Configuration
BHASHINI_PIPELINE_URL = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
BHASHINI_USER_ID = os.environ.get("BHASHINI_USER_ID", "")
BHASHINI_API_KEY = os.environ.get("BHASHINI_API_KEY", "")
BHASHINI_PIPELINE_ID = os.environ.get("BHASHINI_PIPELINE_ID", "")

SUPPORTED_LANGUAGES = {
    'en': {'name': 'English', 'native': 'English'},
    'hi': {'name': 'Hindi', 'native': 'हिन्दी'},
    'gu': {'name': 'Gujarati', 'native': 'ગુજરાતી'},
    'mr': {'name': 'Marathi', 'native': 'मराठी'},
    'bn': {'name': 'Bengali', 'native': 'বাংলা'},
    'ta': {'name': 'Tamil', 'native': 'தமிழ்'},
    'te': {'name': 'Telugu', 'native': 'తెలుగు'}
}

# Pre-compiled high-quality domain responses for Indian languages
# (used directly when Bhashini API key is unconfigured or as offline fallback)
MULTILINGUAL_KNOWLEDGE_BASE = {
    'hi': {
        'greeting': "नमस्ते! मैं सिल्वरबॉट (SilverBot) हूँ, आपका यात्रा सहायक। मैं वरिष्ठ नागरिकों की सुरक्षित और स्वतंत्र यात्रा में कैसे सहायता कर सकता हूँ?",
        'railway': "हमारे सत्यापित साथी रेलवे स्टेशन पर बुजुर्गों को कुली/सामान संभालने, प्लेटफॉर्म नेविगेशन, व्हीलचेयर सहायता, और ट्रेन की सीट तक सुरक्षित बैठाने में मदद करते हैं। क्या आप स्टेशन सहायता बुक करना चाहते हैं?",
        'hospital': "हम अस्पताल चेकअप, ओपीडी टोकन, व्हीलचेयर चलाने और दवा लेने के लिए संवेदनशील साथी प्रदान करते हैं। क्या आप अस्पताल सहायता बुक करना चाहेंगे?",
        'airport': "हवाई अड्डे पर हमारे साथी टर्मिनल प्रवेश, सामान ट्रॉली, सुरक्षा जांच और बोर्डिंग गेट तक वरिष्ठ नागरिकों के साथ रहते हैं। क्या आपको हवाई यात्रा सहायता चाहिए?",
        'safety': "प्रत्येक सिल्वरकेयर साथी पुलिस सत्यापित, पृष्ठभूमि प्रमाणित, और प्राथमिक चिकित्सा व बुजुर्ग देखभाल में प्रशिक्षित होता है। आप पूरे सफर में लाइव जीपीएस भी ट्रैक कर सकते हैं।",
        'price': "सिल्वरकेयर साथी सेवा की शुरुआत ₹450 प्रति यात्रा (3 घंटे तक) की पारदर्शी दर से होती है। भुगतान यात्रा पूरी होने के बाद किया जाता है।",
        'default': "मैं वरिष्ठ नागरिकों को रेलवे स्टेशन, अस्पताल, हवाई अड्डे या प्रशासनिक कार्यों के लिए समर्पित साथी उपलब्ध कराता हूँ। कृपया अपनी आवश्यकता बताएं।"
    },
    'gu': {
        'greeting': "નમસ્તે! હું સિલ્વરબોટ (SilverBot) છું. વરિષ્ઠ નાગરિકોની સલામત અને સ્વતંત્ર મુસાફરીમાં હું તમને કેવી રીતે મદદ કરી શકું?",
        'railway': "અમારા વેરિફાઇડ સાથીઓ રેલ્વે સ્ટેશન પર વડીલોને સામાન સંભાળવા, પ્લેટફોર્મ માર્ગદર્શન, વ્હીલચેર અને ટ્રેનમાં સીટ સુધી બેસાડવામાં મદદ કરે છે.",
        'hospital': "હોસ્પિટલ ઓપીડી, વ્હીલચેર સહાય અને દવા લેવા માટે અમે સંવેદનશીલ સહાયક પૂરા પાડીએ છીએ. શું તમારે હોસ્પિટલ સહાય બુક કરવી છે?",
        'airport': "એરપોર્ટ પર ટર્મિનલ એન્ટ્રી, સામાન અને બોર્ડિંગ ગેટ સુધી અમારા સાથી વડીલો સાથે રહે છે.",
        'safety': "દરેક સાથી પોલીસ ચકાસાયેલ છે અને ફર્સ્ટ-એઇડમાં પ્રશિક્ષિત છે. પરિવાર માટે લાઈવ જીપીએસ ટ્રેકિંગ ઉપલબ્ધ છે.",
        'price': "સિલ્વરકેર સેવા માત્ર ₹450 થી શરૂ થાય છે. મુસાફરી પૂર્ણ થયા પછી જ પેમેન્ટ કરવાનું રહે છે.",
        'default': "હું વરિષ્ઠ નાગરિકો માટે સલામત સાથી બુક કરવામાં મદદ કરું છું. કૃપા કરીને તમારી મુસાફરી વિગત જણાવો."
    },
    'mr': {
        'greeting': "नमस्कार! मी सिल्व्हरबॉट (SilverBot) आहे. ज्येष्ठ नागरिकांच्या सुरक्षित प्रवासात मी तुम्हाला कशी मदत करू शकतो?",
        'railway': "आमचे पडताळणी केलेले सहकारी रेल्वे स्थानकावर ज्येष्ठ नागरिकांना सामान व्यवस्थापन, व्हीलचेअर आणि ट्रेनच्या डब्यापर्यंत पोहोचवण्यात मदत करतात.",
        'hospital': "हॉस्पिटल तपासणी, व्हीलचेअर चालवणे आणि औषधे गोळा करण्यासाठी आम्ही काळजीवाहू सहकारी देतो.",
        'airport': "विमानतळावर लगेज, सुरक्षा तपासणी आणि बोर्डिंग गेटपर्यंत आमचे साथीदार ज्येष्ठांना पूर्ण मदत करतात.",
        'safety': "प्रत्येक सहकारी पोलीस पडताळणी केलेला असून प्रथमोपचार व ज्येष्ठ नागरिकांच्या सेवेत प्रशिक्षित आहे.",
        'price': "सिल्व्हरकेअर सेवा फक्त ₹450 (3 तासांपर्यंत) पासून सुरू होते. प्रवास सुरक्षित पूर्ण झाल्यावरच पेमेंट द्या.",
        'default': "ज्येष्ठ नागरिकांसाठी रेल्वे, रुग्णालय किंवा इतर प्रवासासाठी सुरक्षित साथीदार मिळवण्यासाठी मी येथे आहे."
    },
    'bn': {
        'greeting': "নমস্কার! আমি সিলভারবট (SilverBot)। প্রবীণ নাগরিকদের নিরাপদ ও স্বাধীন ভ্রমণে আমি কীভাবে সাহায্য করতে পারি?",
        'railway': "আমাদের ভেরিফাইড সঙ্গীরা রেলওয়ে স্টেশনে লাগেজ, প্ল্যাটফর্ম নেভিগেশন, হুইলচেয়ার এবং ট্রেনের সিটে উঠতে সাহায্য করেন।",
        'hospital': "হাসপাতাল চেকআপ, ডাক্তারের লাইন এবং হুইলচেয়ার সহায়তার জন্য আমরা যত্নশীল সঙ্গী প্রদান করি।",
        'airport': "এয়ারপোর্টে লাগেজ ট্রলি, সুরক্ষা চেক এবং বোর্ডিং গেট পর্যন্ত আমাদের সঙ্গীরা সহায়তা করেন।",
        'safety': "আমাদের প্রত্যেক সঙ্গী পুলিশ যাচাইকৃত এবং প্রাথমিক চিকিৎসা ও প্রবীণ সেবায় প্রশিক্ষিত। সম্পূর্ণ লাইভ জিপিএস ট্র্যাকিং পাওয়া যায়।",
        'price': "সিলভারকেয়ার সহায়তা মাত্র ₹৪৫০ থেকে শুরু হয়। ভ্রমণ নিরাপদে সম্পন্ন হওয়ার পর পেমেন্ট করা যায়।",
        'default': "রেলওয়ে স্টেশন, হাসপাতাল বা এয়ারপোর্টের জন্য প্রবীণ নাগরিকদের সঙ্গী বুক করতে আমাকে জানান।"
    },
    'ta': {
        'greeting': "வணக்கம்! நான் சில்வர்பாட் (SilverBot). மூத்த குடிமக்களின் பாதுகாப்பான பயணத்திற்கு நான் எவ்வாறு உதவ முடியும்?",
        'railway': "ரயில் நிலையங்களில் லக்கேஜ், பிளாட்பார்ம் வழிநடத்துதல், சக்கர நாற்காலி மற்றும் ரயிலில் ஏறுவதற்கு எங்கள் சரிபார்க்கப்பட்ட தோழர்கள் உதவுகிறார்கள்.",
        'hospital': "மருத்துவமனை பரிசோதனைகள், வரிசையில் நிற்றல் மற்றும் சக்கர நாற்காலி உதவிக்கு கனிவான தோழர்களை வழங்குகிறோம்.",
        'airport': "விமான நிலையத்தில் லக்கேஜ் டிராலி மற்றும் போர்டிங் கேட் வரை மூத்த குடிமக்களுடன் எங்கள் தோழர்கள் உடனிருக்கிறார்கள்.",
        'safety': "அனைத்து தோழர்களும் காவல் துறையினரால் சரிபார்க்கப்பட்டு முதல் உதவி பயிற்சி பெற்றவர்கள். குடும்பத்தினருக்கு நேரலை ஜிபிஎஸ் வசதி உள்ளது.",
        'price': "பயணக் கட்டணம் ₹450 முதல் தொடங்குகிறது. பயணம் பாதுகாப்பாக முடிந்த பிறகு பணம் செலுத்தலாம்.",
        'default': "மூத்த குடிமக்கள் எளிதாகவும் பாதுகாப்பாகவும் பயணிக்க உதவ நான் தயாராக உள்ளேன்."
    },
    'te': {
        'greeting': "నమస్కారం! నేను సిల్వర్‌బాట్ (SilverBot). సీనియర్ సిటిజన్ల సురక్షిత ప్రయాణానికి నేను ఎలా సహాయపడగలను?",
        'railway': "రైల్వే స్టేషన్లలో లగేజీ, ప్లాట్‌ఫారమ్ మార్గదర్శకత్వం, వీల్‌చైర్ సహాయం కోసం మా వెరిఫైడ్ కంపానియన్లు సహాయం చేస్తారు.",
        'hospital': "హాస్పిటల్ చెకప్‌లు, వీల్‌చైర్ సహాయం మరియు మందులు తీసుకోవడంలో మా సహచరులు అండగా ఉంటారు.",
        'airport': "విమానాశ్రయంలో లగేజ్ మరియు బోర్డింగ్ గేట్ వరకు సీనియర్ సిటిజన్లకు సంరక్షణగా తోడుంటారు.",
        'safety': "మా కంపానియన్లు అందరూ పోలీస్ వెరిఫై చేయబడినవారు మరియు ఫస్ట్ ఎయిడ్ శిక్షణ పొందినవారు.",
        'price': "సహాయ సేవా రుసుము కేవలం ₹450 నుండి ప్రారంభం. ప్రయాణం పూర్తయిన తర్వాత చెల్లించవచ్చు.",
        'default': "రైల్వే స్టేషన్, ఆసుపత్రి లేదా విమానాశ్రయానికి ప్రయాణ సహచరులను బుక్ చేసుకోవడానికి నన్ను అడగండి."
    },
    'en': {
        'greeting': "Hello! I am SilverBot, your multilingual travel guide powered by Bhashini AI. How can I help you or your family member travel safely today?",
        'railway': "Our verified companions assist elders at railway stations with coolie/luggage coordination, platform navigation, wheelchair handling, and finding their seat and coach.",
        'hospital': "We provide patient and caring companions for hospital checkups, queue standing, wheelchair support, and pharmacy guidance.",
        'airport': "For airport travel, companions assist with terminal entry, luggage trolley handling, security check accompaniment, and boarding gate navigation.",
        'safety': "Every Silvercare companion undergoes 3-step verification: Government ID, police verification, and elderly empathy & emergency first-aid training.",
        'price': "Silvercare companion assistance starts from a transparent flat rate of ₹450 per journey (up to 3 hours). Payment is completed safely after safe drop-off.",
        'default': "I'm here to help elderly citizens travel with dignity and independence. You can book a verified companion for railway stations, hospitals, airports, or daily errands with complete live tracking."
    }
}

def translate_with_bhashini(text, source_lang, target_lang):
    """
    Calls MeitY Bhashini Dhruva / ULCA Inference Pipeline API for NMT (Translation).
    Falls back gracefully if credentials are not configured.
    """
    if not (BHASHINI_USER_ID and BHASHINI_API_KEY and BHASHINI_PIPELINE_ID):
        # Credentials not set; fallback engine handles translation
        return None

    try:
        payload = {
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": {
                        "language": {
                            "sourceLanguage": source_lang,
                            "targetLanguage": target_lang
                        }
                    }
                }
            ],
            "inputData": {
                "input": [
                    {
                        "source": text
                    }
                ]
            }
        }

        req = urllib.request.Request(
            BHASHINI_PIPELINE_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                "Content-Type": "application/json",
                "userID": BHASHINI_USER_ID,
                "ulcaApiKey": BHASHINI_API_KEY,
                "pipelineId": BHASHINI_PIPELINE_ID
            }
        )

        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            output_text = res_data['pipelineResponse'][0]['output'][0]['target']
            return output_text
    except Exception as e:
        print(f"Bhashini API call notice: {e}")
        return None

def process_bhashini_chat(message, language='en'):
    """
    Processes chat message in chosen Indian language using Bhashini pipeline or multilingual knowledge base.
    """
    lang = language.lower()
    if lang not in SUPPORTED_LANGUAGES:
        lang = 'en'

    msg_lower = message.strip().lower()

    # Determine intent
    intent = 'default'
    if not msg_lower:
        intent = 'greeting'
    elif any(k in msg_lower for k in ['railway', 'train', 'station', 'रेल', 'ट्रेन', 'स्टेशन', 'ரயில்', 'రైలు', 'রেল']):
        intent = 'railway'
    elif any(k in msg_lower for k in ['hospital', 'doctor', 'clinic', 'अस्पताल', 'डॉक्टर', 'హాస్పిటల్', 'மருத்துவமனை', 'হাসপাতাল']):
        intent = 'hospital'
    elif any(k in msg_lower for k in ['airport', 'flight', 'हवाई', 'विमान', 'விமானம்', 'విమానం', 'বিমান']):
        intent = 'airport'
    elif any(k in msg_lower for k in ['safety', 'verify', 'police', 'सुरक्षा', 'सत्यापित', 'போலீஸ்', 'రక్షణ']):
        intent = 'safety'
    elif any(k in msg_lower for k in ['price', 'cost', 'fare', 'पैसा', 'किराया', 'రూపాయలు', 'கட்டணம்', 'টাকা']):
        intent = 'price'

    # Check if live Bhashini API can translate
    live_translation = None
    if BHASHINI_API_KEY and lang != 'en':
        base_en_reply = MULTILINGUAL_KNOWLEDGE_BASE['en'].get(intent, MULTILINGUAL_KNOWLEDGE_BASE['en']['default'])
        live_translation = translate_with_bhashini(base_en_reply, 'en', lang)

    if live_translation:
        reply = live_translation
    else:
        # Use native response from multilingual engine
        lang_dict = MULTILINGUAL_KNOWLEDGE_BASE.get(lang, MULTILINGUAL_KNOWLEDGE_BASE['en'])
        reply = lang_dict.get(intent, lang_dict['default'])

    # Determine action prefill suggestions
    action_type = None
    action_asst = None
    if intent == 'railway':
        action_type = 'Railway Station'
        action_asst = 'Luggage Support, Wheelchair Assistance, Ticket Guidance'
    elif intent == 'hospital':
        action_type = 'Hospital'
        action_asst = 'Wheelchair Assistance, Walking Support'
    elif intent == 'airport':
        action_type = 'Airport'
        action_asst = 'Luggage Support, Wheelchair Assistance'

    return {
        'reply': reply,
        'language': lang,
        'language_name': SUPPORTED_LANGUAGES[lang]['name'],
        'action_type': action_type,
        'action_asst': action_asst
    }
