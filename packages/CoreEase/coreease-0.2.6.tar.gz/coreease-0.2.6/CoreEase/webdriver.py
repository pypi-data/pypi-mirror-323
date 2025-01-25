from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import InvalidArgumentException
def StartBrowser(optiontruefalse):
    global browser
    browserheadless = Options()
    browserheadless.add_argument("--headless")
    if optiontruefalse == True:
        browser=webdriver.Firefox(options=browserheadless)
    if optiontruefalse == False:
        browser=webdriver.Firefox()
def CloseBrowser():
    browser.quit()
def ClickButton(button):
    try:
        button.click()
    except Exception:
        pass
def GoToUrl(urlnewtarget):
    try:
        browser.get(urlnewtarget)
        return True
    except InvalidArgumentException:
        return None 
def OnlinePortalLoginTry(usernameentryfield,passwordentryfield,submitbutton,username,password):
    check0 = browser.title
    usernameentryfield.send_keys(username)
    passwordentryfield.send_keys(password)
    submitbutton.click()
    check1 = browser.title
    if check1 == check0:
        return None
    else:
        return True
def DetectChangeinWebsite():
    domold = browser.page_source
    domnew = browser.page_source
    if domnew != domold:
        return False
    return True
def ParseforLoginEntrysandSubmitButton():
    strusernameforsearch = "username"
    strpasswordforsearch = "password"
    strbuttonforsearch = "submit"
    elementstocheck = ["a","button","div","span","form","li","area","svg a","input","img","details","summary","nav","section","article","header","footer","select","textarea","label","option","optgroup","output","progress","meter","input[type='file']","input[type='radio']","input[type='checkbox']","input[type='button']","input[type='submit']","input[type='reset']"]
    attributestocheck = ["href","onclick","action","method","id","class","name","type","placeholder","value","src","alt","title","disabled","checked","readonly","required","maxlength","min","max","step","pattern","role","aria-label","aria-hidden","style","data-*","target","rel","download","xlink:href"]
    for element in elementstocheck:
        x = browser.find_elements(By.CSS_SELECTOR, element)
        for y in x:
            for attribute in attributestocheck:
                z = y.get_attribute(attribute)
                if z != None:
                    if strusernameforsearch.lower() in z.lower():
                        usernameentryfield = y
                    if strpasswordforsearch.lower() in z.lower():
                        passwordentryfield = y
                    if strbuttonforsearch.lower() in z.lower():
                        submitbutton = y
    try:
        return usernameentryfield, passwordentryfield, submitbutton
    except UnboundLocalError:
        try:
            return None, passwordentryfield, submitbutton
        except UnboundLocalError:
            try:
                return None, None, submitbutton
            except UnboundLocalError:
                try:
                    return usernameentryfield, None, submitbutton
                except UnboundLocalError:
                    try:
                        return usernameentryfield, passwordentryfield, None
                    except UnboundLocalError:
                        try:
                            return None, passwordentryfield, None
                        except UnboundLocalError:
                            try:
                                return usernameentryfield, None, None
                            except UnboundLocalError:
                                return None, None, None
def ParseforLinks():
    httplinklist = []
    httpslinklist = []
    strhttpsearch = "http://"
    strhttpssearch = "https://"
    elementstocheck = ["a","button","div","span","form","li","area","svg a","input","img","details","summary","nav","section","article","header","footer","select","textarea","label","option","optgroup","output","progress","meter","input[type='file']","input[type='radio']","input[type='checkbox']","input[type='button']","input[type='submit']","input[type='reset']"]
    attributestocheck = ["href","onclick","action","method","id","class","name","type","placeholder","value","src","alt","title","disabled","checked","readonly","required","maxlength","min","max","step","pattern","role","aria-label","aria-hidden","style","data-*","target","rel","download","xlink:href"]
    for element in elementstocheck:
        x = browser.find_elements(By.CSS_SELECTOR, element)
        for y in x:
            for attribute in attributestocheck:
                z = y.get_attribute(attribute)
                if z != None:
                    if strhttpsearch.lower() in z.lower():
                        if z not in httplinklist:
                            httplinklist.append(y.text)
                            httplinklist.append(z)
                    if strhttpssearch.lower() in z.lower():
                        if z not in httpslinklist:
                            httpslinklist.append(y.text)
                            httpslinklist.append(z)
    return httplinklist, httpslinklist
def ParseforButtons():
    buttonlist = []
    elementstocheck = ["button","input[type='button']","input[type='submit']","input"]
    attributestocheck = ["id"]
    for element in elementstocheck:
        x = browser.find_elements(By.CSS_SELECTOR, element)
        for y in x:
            for attribute in attributestocheck:
                z = y.get_attribute(attribute)
                if z != None:
                    if z not in buttonlist:
                        buttonlist.append(z)
                    if y not in buttonlist:
                        buttonlist.append(y)
    return buttonlist