import { useEffect, useState } from "react";
import { translations } from "./translations";

export const LANGUAGE_STORAGE_KEY = "udyamsaathi_language";
export const isKannada = (text = "") => /[\u0C80-\u0CFF]/.test(text);

export function localizeDynamic(value, language) {
  if (language !== "kn" || !value) return value;
  const replacements = {
    "Dairy Farming": "ಹೈನುಗಾರಿಕೆ",
    "Poultry Farming": "ಕೋಳಿ ಸಾಕಾಣಿಕೆ",
    "Goat Farming": "ಮೇಕೆ ಸಾಕಾಣಿಕೆ",
    "Mushroom Farming": "ಅಣಬೆ ಕೃಷಿ",
    "Beekeeping": "ಜೇನು ಸಾಕಾಣಿಕೆ",
    "Organic Vegetable Farming": "ಸಾವಯವ ತರಕಾರಿ ಕೃಷಿ",
    "Nursery": "ಸಸ್ಯ ನರ್ಸರಿ",
    "Vermicomposting": "ಎರೆಹುಳು ಗೊಬ್ಬರ ತಯಾರಿಕೆ",
    "Spice Processing": "ಮಸಾಲೆ ಸಂಸ್ಕರಣೆ",
    "Millet Processing": "ಸಿರಿಧಾನ್ಯ ಸಂಸ್ಕರಣೆ",
    "Food Processing": "ಆಹಾರ ಸಂಸ್ಕರಣೆ",
    "Pickle Making": "ಉಪ್ಪಿನಕಾಯಿ ತಯಾರಿಕೆ",
    "Flour Mill": "ಹಿಟ್ಟು ಗಿರಣಿ",
    "Tailoring": "ಹೊಲಿಗೆ ಕೆಲಸ",
    "Handicrafts": "ಕರಕುಶಲ ವಸ್ತುಗಳು",
    "Bamboo Products": "ಬಿದಿರು ಉತ್ಪನ್ನಗಳು",
    "Rural Bakery": "ಗ್ರಾಮೀಣ ಬೇಕರಿ",
    "Fish Farming": "ಮೀನು ಸಾಕಾಣಿಕೆ",
    "Coconut Products": "ತೆಂಗಿನ ಉತ್ಪನ್ನಗಳು",
    "Agarbatti Manufacturing": "ಅಗರಬತ್ತಿ ತಯಾರಿಕೆ",
    "Mobile Repair and Digital Service Center": "ಮೊಬೈಲ್ ದುರಸ್ತಿ ಮತ್ತು ಡಿಜಿಟಲ್ ಸೇವಾ ಕೇಂದ್ರ",
    "Karnataka Rural Enterprise Starter Support": "ಕರ್ನಾಟಕ ಗ್ರಾಮೀಣ ಉದ್ಯಮ ಆರಂಭಿಕ ಬೆಂಬಲ",
    "Agri Livelihood Equipment Support": "ಕೃಷಿ ಜೀವನೋಪಾಯ ಉಪಕರಣ ಬೆಂಬಲ",
    "Livestock Starter Kit": "ಪಶುಸಂಗೋಪನಾ ಆರಂಭಿಕ ಕಿಟ್",
    "Resident of Karnataka": "ಕರ್ನಾಟಕದ ನಿವಾಸಿ",
    "New rural enterprise": "ಹೊಸ ಗ್ರಾಮೀಣ ಉದ್ಯಮ",
    "Basic business plan": "ಮೂಲಭೂತ ವ್ಯವಹಾರ ಯೋಜನೆ",
    "Agriculture-related activity": "ಕೃಷಿ ಸಂಬಂಧಿತ ಚಟುವಟಿಕೆ",
    "Owns or leases farm land": "ಕೃಷಿ ಜಮೀನು ಹೊಂದಿರುವುದು ಅಥವಾ ಗುತ್ತಿಗೆಗೆ ಪಡೆದಿರುವುದು",
    "Animal care plan": "ಪ್ರಾಣಿ ಆರೈಕೆ ಯೋಜನೆ",
    "Access to water and shelter": "ನೀರು ಮತ್ತು ಆಶ್ರಯದ ಸೌಲಭ್ಯ",
    "Identity proof": "ಗುರುತಿನ ಪುರಾವೆ",
    "Address proof": "ವಿಳಾಸದ ಪುರಾವೆ",
    "Land or lease record": "ಜಮೀನು ಅಥವಾ ಗುತ್ತಿಗೆ ದಾಖಲೆ",
    "Business plan": "ವ್ಯವಹಾರ ಯೋಜನೆ",
    "Location proof": "ಸ್ಥಳದ ಪುರಾವೆ",
    "Quotation": "ಬೆಲೆ ಉಲ್ಲೇಖ",
    "Animal care plan": "ಪ್ರಾಣಿ ಆರೈಕೆ ಯೋಜನೆ",
    "Premises proof": "ಆವರಣದ ಪುರಾವೆ",
    "Bank details": "ಬ್ಯಾಂಕ್ ವಿವರಗಳು",
    "Local authority / Animal Husbandry office": "ಸ್ಥಳೀಯ ಪ್ರಾಧಿಕಾರ / ಪಶುಸಂಗೋಪನಾ ಕಚೇರಿ",
    "Local authority": "ಸ್ಥಳೀಯ ಪ್ರಾಧಿಕಾರ",
    "District Industries Centre / Local authority": "ಜಿಲ್ಲಾ ಕೈಗಾರಿಕಾ ಕೇಂದ್ರ / ಸ್ಥಳೀಯ ಪ್ರಾಧಿಕಾರ",
    "Review the ": "ಪರಿಶೀಲಿಸಿ: ",
    "Your available capital matches the estimated requirement": "ನಿಮ್ಮ ಲಭ್ಯವಿರುವ ಬಂಡವಾಳವು ಅಂದಾಜು ಅಗತ್ಯಕ್ಕೆ ಹೊಂದಿಕೆಯಾಗುತ್ತದೆ",
    "Your animal care skill is relevant": "ನಿಮ್ಮ ಪ್ರಾಣಿ ಆರೈಕೆ ಕೌಶಲ್ಯವು ಸಂಬಂಧಿಸಿದೆ",
    "Your available land and water resources are suitable": "ನಿಮ್ಮ ಜಮೀನು ಮತ್ತು ನೀರಿನ ಸಂಪನ್ಮೂಲಗಳು ಸೂಕ್ತವಾಗಿವೆ",
    "The business is planned for Karnataka, matching your location": "ಈ ವ್ಯವಹಾರವು ಕರ್ನಾಟಕಕ್ಕೆ ಯೋಜಿಸಲಾಗಿದೆ ಮತ್ತು ನಿಮ್ಮ ಸ್ಥಳಕ್ಕೆ ಹೊಂದಿಕೆಯಾಗುತ್ತದೆ",
    "Capital subsidy": "ಬಂಡವಾಳ ಸಹಾಯಧನ",
    "Equipment support": "ಉಪಕರಣ ಬೆಂಬಲ",
    "Asset support": "ಆಸ್ತಿ ಬೆಂಬಲ",
    "Udyam Registration": "ಉದ್ಯಮ ನೋಂದಣಿ",
    "Local trade registration": "ಸ್ಥಳೀಯ ವ್ಯಾಪಾರ ನೋಂದಣಿ",
    "Livestock activity permission": "ಪಶುಸಂಗೋಪನಾ ಚಟುವಟಿಕೆ ಅನುಮತಿ",
    "Food business registration": "ಆಹಾರ ವ್ಯವಹಾರ ನೋಂದಣಿ",
    "Review the Goat Farming recommendation and its prototype suitability score.": "ಮೇಕೆ ಸಾಕಾಣಿಕೆ ಶಿಫಾರಸು ಮತ್ತು ಅದರ ಮೂಲಮಾದರಿ ಹೊಂದಾಣಿಕೆ ಅಂಕವನ್ನು ಪರಿಶೀಲಿಸಿ.",
    "Set aside the estimated initial investment and confirm the operating budget.": "ಅಂದಾಜು ಆರಂಭಿಕ ಹೂಡಿಕೆಯನ್ನು ಮೀಸಲಿಟ್ಟು ಕಾರ್ಯಾಚರಣಾ ಬಜೆಟ್ ಪರಿಶೀಲಿಸಿ.",
    "Explore financing options for the estimated capital gap.": "ಅಂದಾಜು ಹೂಡಿಕೆ ಕೊರತೆಯಿಗಾಗಿ ಹಣಕಾಸಿನ ಆಯ್ಕೆಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.",
    "Check the suitable support records and verify details with official sources before applying.": "ಸೂಕ್ತ ಬೆಂಬಲ ದಾಖಲೆಗಳನ್ನು ಪರಿಶೀಲಿಸಿ ಮತ್ತು ಅರ್ಜಿ ಸಲ್ಲಿಸುವ ಮೊದಲು ಅಧಿಕೃತ ಮೂಲಗಳಲ್ಲಿ ವಿವರಗಳನ್ನು ದೃಢಪಡಿಸಿ.",
    "Prepare the listed documents and complete the applicable registration or approval.": "ಪಟ್ಟಿಯಲ್ಲಿರುವ ದಾಖಲೆಗಳನ್ನು ಸಿದ್ಧಪಡಿಸಿ ಮತ್ತು ಅನ್ವಯಿಸುವ ನೋಂದಣಿ ಅಥವಾ ಅನುಮತಿಯನ್ನು ಪೂರ್ಣಗೊಳಿಸಿ.",
    "Confirm required registrations and approvals with the relevant local authority.": "ಅಗತ್ಯ ನೋಂದಣಿ ಮತ್ತು ಅನುಮತಿಗಳನ್ನು ಸಂಬಂಧಿತ ಸ್ಥಳೀಯ ಅಧಿಕಾರಿಯಿಂದ ದೃಢಪಡಿಸಿ.",
    "Begin business setup only after confirming costs, support, and approvals.": "ವೆಚ್ಚ, ಬೆಂಬಲ ಮತ್ತು ಅನುಮತಿಗಳನ್ನು ದೃಢಪಡಿಸಿದ ನಂತರ ಮಾತ್ರ ವ್ಯವಹಾರ ಪ್ರಾರಂಭಿಸಿ.",
    "Check official sources for support that may apply to this business.": "ಈ ವ್ಯವಹಾರಕ್ಕೆ ಅನ್ವಯಿಸಬಹುದಾದ ಬೆಂಬಲಕ್ಕಾಗಿ ಅಧಿಕೃತ ಮೂಲಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.",
  };
  if (value.startsWith("Review the ") && value.endsWith(" recommendation and its prototype suitability score.")) {
    const business = value.slice("Review the ".length, -" recommendation and its prototype suitability score.".length);
    return `${localizeDynamic(business, language)} ಶಿಫಾರಸು ಮತ್ತು ಅದರ ಮೂಲಮಾದರಿ ಹೊಂದಾಣಿಕೆ ಅಂಕವನ್ನು ಪರಿಶೀಲಿಸಿ.`;
  }
  return replacements[value] || value;
}

export function useLanguage() {
  const [language, setLanguageState] = useState("en");

  useEffect(() => {
    const stored = window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
    if (stored === "en" || stored === "kn") setLanguageState(stored);
  }, []);

  const setLanguage = (nextLanguage) => {
    const next = nextLanguage === "kn" ? "kn" : "en";
    setLanguageState(next);
    window.localStorage.setItem(LANGUAGE_STORAGE_KEY, next);
  };

  const t = (path, values = {}) => {
    const value = path.split(".").reduce((current, key) => current?.[key], translations[language]) ?? path;
    return Object.entries(values).reduce((result, [key, replacement]) => result.replaceAll(`{${key}}`, String(replacement)), value);
  };

  return { language, setLanguage, t };
}
