if __package__ in {None, ""}:
    from extract_account_balance.app import main
else:
    from .app import main


if __name__ == "__main__":
    main()
