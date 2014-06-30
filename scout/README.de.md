# scout – Prüfe die Integrität von der initrd und entschlüssle das root Dateisystem aus der Ferne

Dieses Skript ermöglicht das Entschlüsseln von Vollverschlüsselten Linux Systemen über SSH nachdem sichergestellt wurde, dass die initrd nicht manipuliert wurde.
Das Script ist eine neu Implementierung in Python auf Basis des Bash Skripts scout.bash, welches sich im Verzeichnis scout-bash befindet. Es dient zum Vergleich und um nähere Dokumentation zu erhalten.

## Liste von Vorteilen zur Bash Implementierung

* Es werden nicht mehr SSH Verbindungen aufgebaut als nötig.
* Verbesserte Fehlerbehandlung mit pexpect (es wird ein bestimmtes Verhalten von der remote Shell erwartet und darauf getestet).
* Sauberere Implementierung, welche eine einfache Erweiterbarkeit erlaubt.
* Das Password zur Entschlüsselung kann aus einer Konfigurationsdatei gelesen werden.
* Zusätzliche sicherheitsbezogene Funktionen kommen eventuell in der Zukunft (siehe [ToDo Liste][todo]).

## Liste von Nachteilen

* Mehr Software Abhängigkeiten auf dem Client System.
* Bislang nur mit Debian stable über mehrere Monate getestet. Es sind eventuell Anpassungen notwendig, wenn andere Systeme benutzt werden (hauptsächlich, da ich relativ paranoid bin und gegen bestimme Versionsnummern teste. Ist auf der [Todo Liste][todo]).

[todo]: scout/#todo
