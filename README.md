# プロジェクトの詳細

#### ＜共通＞
- MS1ページ：[テーマ1の説明](https://app.ms1.com/academy/1BYJipoSWFWcxfxUIoruQ6/4NBJkylZbtUd6Wxtpw4nbE/5VDANh8J5d2NltgkZUPyTk/2f4kqS0Gcl75ANeD8HK9bv/1XS6qWijKAPuZWKx9kY0K8) 、 [修了プロジェクトのガイドライン](https://app.ms1.com/academy/1BYJipoSWFWcxfxUIoruQ6/4NBJkylZbtUd6Wxtpw4nbE/5VDANh8J5d2NltgkZUPyTk/5pbSGNRYpiaKlCctj9PaET/jBpJOZ9FVVT7qyahWPMEk)
- [7/22(月)のキックオフスライド](https://toyotaglobal.enterprise.slack.com/files/U04M3KX6CP2/F07DGHBRMDJ/____________________________________________________________.pdf)

#### ＜グループ1内の計画＞
- **[★修了プロジェクト計画（7/29提出）](./doc/修了プロジェクト計画.md)**
-  [MS1上の元々のテーマ1との要件比較](./doc/MS1上の元々のテーマ1との要件比較.md)

# 開発情報

#### ＜作業用インフラ＞
- **JIRA**：[チームのJIRAボード](https://rhdojo.atlassian.net/jira/software/projects/PCPG/boards/2)
  - サブチケットを含めた一覧はこちら：[Confluence：ストーリーとサブチケットの一覧](https://rhdojo.atlassian.net/wiki/spaces/~712020ca0f8221407b440b8d4c1a0660e8be32/pages/14188549/JIRA)
- **GitHub Wiki**：[議事録ページ](https://github.com/rhashimoto777/python-capstone-project/wiki/%E8%AD%B0%E4%BA%8B%E9%8C%B2) 、 [TIPS(ノウハウ共有)](https://github.com/rhashimoto777/python-capstone-project/wiki/TIPS%EF%BC%88%E3%83%8E%E3%82%A6%E3%83%8F%E3%82%A6%E5%85%B1%E6%9C%89%EF%BC%89)

<br>

#### ＜各種ポリシー＞
- **文書管理**
    - 設計情報は[「designフォルダ」](./design/)内に配置する。
    - ユーザーストーリーは[「designフォルダ」](./design/)内の[「ユーザーストーリー.md」](./design/ユーザーストーリー.md)に記載する。
    - その他の雑多情報（計画やプレゼンテーションなど）は[「docフォルダ」](./doc/)内に配置する。

- **GitHub Repository管理**
    - mainへの直接pushを禁止する設定にしている。mainに変更を加えるには別branchを作ってPullRequestを発行する。
    - PullRequestのデフォルトレビュワーとして下記メンバが自動追加される。柔軟な状況に対応するため、現状レビュワーからの承認なしでもマージできるようにしている。（基本的にはデフォルトレビュワーから承認されることを目指すのがベター）
        ```
        ・全てのファイル変更：橋本
        ・ユーザーストーリー.mdの変更：尾崎
        ```
    - デフォルトのPRマージ方法は `Squash and merge` とする。
        - メリデメあるものの、あるPRで破壊的な変更が入ったケースにおいて要因となるPRを特定しやすい利点を重視した。
        - 1つのPRの規模は大きくなりすぎないようにすることが望ましい。

- **進捗・残件管理**
    - 水曜・金曜のスタンドアップミーティングで状況を確認する。
        - [参考：MS1上のスタンドアップミーティングのガイドライン](https://app.ms1.com/academy/1BYJipoSWFWcxfxUIoruQ6/4NBJkylZbtUd6Wxtpw4nbE/5VDANh8J5d2NltgkZUPyTk/5pbSGNRYpiaKlCctj9PaET/jBpJOZ9FVVT7qyahWPMEk)
    - スタンドアップミーティング以外でも、可能な限り「着手状況」「困りごと」などをslackで共有し、状況の透明化を目指す。
        - [参考：プロジェクトの潜在的な課題とリスク](https://github.com/rhashimoto777/python-capstone-project/blob/main/doc/%E4%BF%AE%E4%BA%86%E3%83%97%E3%83%AD%E3%82%B8%E3%82%A7%E3%82%AF%E3%83%88%E8%A8%88%E7%94%BB.md#%E8%AA%B2%E9%A1%8C%E3%81%A8%E3%83%AA%E3%82%B9%E3%82%AF)

<br>

#### ＜環境セットアップ＞

- [MS1上の修了プロジェクトのガイドライン](https://app.ms1.com/academy/1BYJipoSWFWcxfxUIoruQ6/4NBJkylZbtUd6Wxtpw4nbE/5VDANh8J5d2NltgkZUPyTk/5pbSGNRYpiaKlCctj9PaET/jBpJOZ9FVVT7qyahWPMEk)の記載を抜粋：
  > リポジトリのREADMEに必要なすべての手順を記述し、誰でも自分のシステムでプロダクトをセットアップして実行できるようにしてください。

- **環境概要**
    - 想定するpython version
      ```
      3.11.0
      ```
        - [参考：Python学習パスのシステムセットアップガイド -  受講者用.pdf](https://toyotaglobal.enterprise.slack.com/files/U04M3KX6CP2/F06L1JN74N7/python___________________________________________________________________-______________.pdf)

    - 使用するライブラリ
      ```
      streamlit
      pandas
      ```
      はデフォルトでは入っていないと思われるため、 `pip install streamlit` などでインストールしてください。

    - streamlitでページを表示するときは、`python main.py` ではなく `streamlit run main.py`で実行してください。


