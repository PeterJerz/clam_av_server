Diese beiden Dateien beschreiben dasselbe Sequenzdiagramm
– einmal als PlantUML (.puml), einmal als Mermaid (.mmd).

Dateien:
- clam_av_architecture_sequence.puml
- clam_av_architecture_sequence.mmd

Rendern (Optionen):
1) VS Code + PlantUML- oder Mermaid-Preview-Extension öffnen.
2) Lokal PlantUML/JAR + Graphviz installieren und dann:
   plantuml clam_av_architecture_sequence.puml
3) Online-Renderer (z.B. Mermaid Live Editor) öffnen und den Inhalt der .mmd einfügen.

Tipp: Das Diagramm zeigt die Pfade INFIZIERT (mit Socket/Queue/Mail)
und CLEAN (keine Aktion), inkl. Lease/Retry-Mechanik der Queue.
