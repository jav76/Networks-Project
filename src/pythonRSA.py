import rsa, time
import logging as log

def genKeys(keySize):
    start = time.time()
    log.info("Generating keys...")
    (public, private) = rsa.newkeys(keySize, poolsize=8)
    try:
        with open("../id_rsa", mode = "wb") as f:
            f.write(private.save_pkcs1())
        with open("../id_rsa.pub", mode = "wb") as f:
            f.write(public.save_pkcs1())
        log.info(f"Finished in {abs(start - time.time()):0.2f}s")
    except:
        log.warning("Could not write keys to file")
    return public, private

def encrypt(msg, key):
    try:
        msg = msg.encode("utf-8", errors="strict")
    except UnicodeError:
        log.warning("Could not encode msg to utf-8")
        return None
    except Exception as e:
        log.warning(e)
        return None
    return rsa.encrypt(msg, key)

def decrypt(msg, key):
    try:
        msg = rsa.decrypt(msg, key)
    except Exception as e:
        log.warning(f"Could not decrypt {msg} : {e}")
        return None
    return msg.decode("utf8")

def encryptFromFile(msg, file = "../id_rsa.pub", key = ""):
    if key == "":
        try:
            with open(file, "rb") as f:
                keyData = f.read()
                f.close()
            pubKey = rsa.PublicKey.load_pkcs1(keyData)
        except FileNotFoundError as e:
            log.warning(f"Could not find id_rsa.pub keyfile {e}")
            return None
        except Exception as e:
            log.warning(f"Could not read id_rsa.pub keyfile {e}")
            return None
    else:
        pubKey = rsa.PublicKey.load_pkcs1(key)
    return encrypt(msg, pubKey)

def decryptFromFile(msg, file = "../id_rsa", key = ""):
    if key == "":
        try:
            with open(file, "rb") as f:
                keyData = f.read()
                f.close()
            privKey = rsa.PrivateKey.load_pkcs1(keyData)
        except FileNotFoundError as e:
            log.warning(f"Could not find id_rsa keyfile {e}")
            return None
        except Exception as e:
            log.warning(f"Could not read id_rsa keyfile {e}")
            return None
    else:
        privKey = rsa.PrivateKey.load_pkcs1(key)
    return decrypt(msg, privKey)