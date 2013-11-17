from bottle import debug, run, default_app

# ... build or import your bottle application here ...
import btchelper

if __name__ == "__main__":
    # bottle run mode
    debug(True)
    run(host='0.0.0.0', port=5050, reloader=True)
else:
    import os
    # Change working directory so relative paths (and template lookup) work again
    os.chdir(os.path.dirname(__file__))

    # Do NOT use bottle.run() with mod_wsgi
    application = default_app()
