"""
Тест конфигурации
"""
from config import print_config, is_testnet, get_config


def main():
    print("=== Тест конфигурации ===\n")
    print_config()

    config = get_config()
    if is_testnet():
        print("\n✅ Настроен Testnet режим")
    else:
        if config['api_key'] == 'your_api_key_here':
            print("\n⚠️  API ключи не установлены!")
            print("Отредактируйте файл .env")
        else:
            print("\n⚠️  ВНИМАНИЕ: Настроен PRODUCTION режим!")


if __name__ == '__main__':
    main()
