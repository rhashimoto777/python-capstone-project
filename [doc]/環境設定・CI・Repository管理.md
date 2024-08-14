# 環境設定

### ＜環境概要＞

|項目|想定環境|
|-|-|
|Python version|3.11.0|
|Linter (静的コード解析)|Ruff <br> Mypy (型チェック用)|
|Formatter (コードの自動整形)|Black <br> isort (モジュールのimport順の修正用) |
<details>
<summary>（参考）Python 3.11.0のインストール方法</summary>

- [参考：Python学習パスのシステムセットアップガイド -  受講者用.pdf](https://toyotaglobal.enterprise.slack.com/files/U04M3KX6CP2/F06L1JN74N7/python___________________________________________________________________-______________.pdf)
</details>

<details>
<summary>（参考）FormatterにもRuffを使わない背景</summary>

- 2023年10月末頃から、RuffにFormatter機能が実装され、Blackとisortの機能を包含しているとのことである。[(参考blog)](https://qiita.com/ciscorn/items/bf78b7ad8e0e332f891b)
- 一方でLocalで試したところisortの機能（import順番の調整）の再現にはRuffにいくらか設定が必要そうであった。
- そのため今回は設定不要の簡便な構成として、Black+isortを採用する。
</details>

<br>

### ＜ライブラリのインストール＞
- 下記コマンドで一括インストールが可能。
    ```
    pip install -r requirements.txt
    ```

<details>
<summary>（参考）requirements.txtの更新方法と注意点</summary>

- requirements.txtの更新自体は下記コマンドで実行できる。
    ```
    pip freeze > requirements.txt

    ```
- 但し、GitHubActions内でもrequirements.txtを用いて環境設定しているため、 `pywin32` `pywinpty` などのWindowsでしか動かないライブラリを含めてしまうとGitHubActionsが止まってしまう。これらは手動で除いてからpushすること。
</details>

<details>
<summary>（参考）仮にLocalの既存のversionと競合する場合は、venv等の仮想環境を活用できる</summary>

- 下記コマンドを実行して環境構築する。（尚、venvフォルダはgit ignoreに追加済）
    ```
    # 仮想環境の作成
    python -m venv venv
    
    # 仮想環境に入る（windowsの場合）
    .\venv\Scripts\activate

    # 仮想環境内でライブラリをインストール
    pip install -r requirements.txt

    # 仮想環境を抜ける
    deactivate
    ```
- 上のコマンドと同様の方法で仮想環境内に入り、各種.pyを実行すれば仮想環境内のライブラリのバージョンが適用される。
</details>

<br>

### ＜ページの表示＞
- streamlitでページを表示するときは、`python main.py` ではなく `streamlit run main.py`を実行する。

<br>

### ＜Local環境でのLinter・Formatter・pytestの適用＞

- **Linter**
    - Ruff
      ```
      ruff check .
      ```
    - Mypy
      ```
      mypy . --ignore-missing-imports --no-namespace-packages
      ```
- **Formatter**
    - Black
      ```
      black .
      ```
    - isort
      ```
      isort .
      ```
- **pytest**
  ```
  pytest
  ```

<br>

# CI（GitHub Actions）
- `main`ブランチへのPRに対して、下記の判定をそれぞれ自動実行する。（合計5個のCIが並列に走る）
    - pytestが全てpassするか
    - Ruffで警告が出ないか
    - Mypyで警告が出ないか
    - Blackで修正箇所が無いか（GitHub上では実際に自動修正するようなpushはされない）
    - isortで修正箇所が無いか（GitHub上では実際に自動修正するようなpushはされない）

<br>

# GitHub Repository管理
- mainへの直接pushを禁止する。(GitHubの設定で操作不可)
mainに変更を加えるには別branchを作ってPullRequest (PR)を発行すること。

<br>

- デフォルトのPRマージ方法は `Squash and merge` とする。
    - `Squash and merge` にはメリデメあるものの、あるPRで破壊的な変更が入ったケースにおいて要因となるPRを特定しやすい利点を重視する。

<br>

- PRのデフォルトレビュワーとして下記メンバを設定する。
    ```
    ・全てのファイル変更：橋本
    ・ユーザーストーリー.mdの変更：尾崎
    ```