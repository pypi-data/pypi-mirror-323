# JijZeptSDK

JijZeptSDKとは、Jijが提供する無償のパッケージ群をまとめてインストールできるPythonパッケージです。使い方は [PyPI.md](PyPI.md) を、含まれるPythonパッケージは [pyproject.toml](pyproject.toml) を参照してください。

## 依存関係の更新について

JijZeptSDKの依存関係は日次で自動更新されるようになっています。具体的には以下のようになっています。詳しくは、 [dependabot.yaml](.github/dependabot.yaml) と [dependabot_auto_merge.yaml](.github/workflows/dependabot_auto_merge.yaml) を確認してください。

> [!IMPORTANT]
> 上記のDependabotはメジャーバージョンアップデートを対象外としています。そのため、メジャーバージョンアップデートの際は手作業で更新を行うようにしてください。

## リリースについて

JijZeptSDKのリリースは週次で自動的に行われるようになっています。詳しくは、 [weekly_release.yaml](.github/workflows/weekly_release.yaml) を確認してください。

> [!WARNING]
> [weekly_release.yaml](.github/workflows/weekly_release.yaml) では、リリース前に依存関係の確認を行うようにしていますが、万が一、リリース後に問題が発覚した場合は以下のように対処してください。
> 1. （既にその日付でリリースされている場合）リリース・タグ・PyPIの該当バージョンを削除してください
> 2. [weekly_release.yaml](.github/workflows//weekly_release.yaml) のWorkflowDispatchでワークフローを起動してください

