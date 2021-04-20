import rsa, time
import logging as log

def genKeys(keySize):
    start = time.time()
    log.info("Generating keys...")
    (public, private) = rsa.newkeys(keySize, poolsize=8)
    try:
        with open("id_rsa", mode = "wb") as f:
            f.write(private.save_pkcs1())
        with open("id_rsa.pub", mode = "wb") as f:
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
        log.error(e)
        return None
    return rsa.encrypt(msg, key)


def decrypt(msg, key):
    try:
        msg = rsa.decrypt(msg, key)
    except Exception as e:
        log.error(f"Could not decrypt {msg} : {e}")
        return None
    return msg.decode("utf8")