import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const FutbolTriviaApp());
}

class FutbolTriviaApp extends StatelessWidget {
  const FutbolTriviaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Futbol Trivia',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1B5E20)),
        useMaterial3: true,
      ),
      home: const PantallaInicio(),
    );
  }
}

class PantallaInicio extends StatelessWidget {
  const PantallaInicio({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF1B5E20), Color(0xFF4CAF50)],
          ),
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.sports_soccer, size: 100, color: Colors.white),
              const SizedBox(height: 20),
              const Text('Futbol Trivia', style: TextStyle(fontSize: 40, fontWeight: FontWeight.bold, color: Colors.white)),
              const SizedBox(height: 10),
              const Text('LaLiga Edition', style: TextStyle(fontSize: 18, color: Colors.white70)),
              const SizedBox(height: 60),
              ElevatedButton(
                onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const MenuJuegos())),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.white,
                  foregroundColor: const Color(0xFF1B5E20),
                  padding: const EdgeInsets.symmetric(horizontal: 50, vertical: 15),
                  textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                child: const Text('Jugar Solo'),
              ),
              const SizedBox(height: 15),
              OutlinedButton(
                onPressed: () {},
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.white,
                  side: const BorderSide(color: Colors.white),
                  padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 15),
                  textStyle: const TextStyle(fontSize: 18),
                ),
                child: const Text('Multijugador'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class MenuJuegos extends StatelessWidget {
  const MenuJuegos({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Elige un juego'),
        backgroundColor: const Color(0xFF1B5E20),
        foregroundColor: Colors.white,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _tarjetaJuego(context, 'Trivia Histórica', 'Preguntas de LaLiga', Icons.quiz, const Color(0xFF1565C0), const PantallaTrivia()),
            _tarjetaJuego(context, 'Adivina el Jugador', 'Pistas progresivas', Icons.person_search, const Color(0xFF6A1B9A), const PantallaAdivinaJugador()),
            _tarjetaJuego(context, 'Adivina el Escudo', 'Identifica el equipo', Icons.shield, const Color(0xFFE65100), const PantallaAdivinaEscudo()),
            _tarjetaJuego(context, 'Completa el Once', 'Próximamente', Icons.group, const Color(0xFF00695C), null),
          ],
        ),
      ),
    );
  }

  Widget _tarjetaJuego(BuildContext context, String titulo, String subtitulo, IconData icono, Color color, Widget? pantalla) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: ListTile(
        leading: CircleAvatar(backgroundColor: color, child: Icon(icono, color: Colors.white)),
        title: Text(titulo, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        subtitle: Text(subtitulo),
        trailing: const Icon(Icons.arrow_forward_ios),
        onTap: pantalla != null
            ? () => Navigator.push(context, MaterialPageRoute(builder: (_) => pantalla))
            : null,
      ),
    );
  }
}

// ─── TRIVIA ───────────────────────────────────────────────────────────────────

class PantallaTrivia extends StatefulWidget {
  const PantallaTrivia({super.key});

  @override
  State<PantallaTrivia> createState() => _PantallaTriviaState();
}

class _PantallaTriviaState extends State<PantallaTrivia> {
  List preguntas = [];
  int indice = 0;
  int puntuacion = 0;
  bool cargando = true;
  String? seleccionada;
  bool respondida = false;

  @override
  void initState() {
    super.initState();
    cargarPreguntas();
  }

  Future<void> cargarPreguntas() async {
    final response = await http.get(Uri.parse('http://localhost:8000/preguntas/trivia?limite=10'));
    if (response.statusCode == 200) {
      setState(() {
        preguntas = json.decode(response.body);
        cargando = false;
      });
    }
  }

  void responder(String opcion) {
    if (respondida) return;
    setState(() {
      seleccionada = opcion;
      respondida = true;
      if (opcion == preguntas[indice]['respuesta_correcta']) puntuacion += 10;
    });
    Future.delayed(const Duration(seconds: 2), () {
      if (indice < preguntas.length - 1) {
        setState(() { indice++; seleccionada = null; respondida = false; });
      } else {
        Navigator.pushReplacement(context, MaterialPageRoute(
          builder: (_) => PantallaResultado(puntuacion: puntuacion, total: preguntas.length * 10, titulo: 'Trivia Histórica'),
        ));
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    if (cargando) return const Scaffold(body: Center(child: CircularProgressIndicator()));
    if (preguntas.isEmpty) return const Scaffold(body: Center(child: Text('No hay preguntas')));

    final pregunta = preguntas[indice];
    final opciones = List<String>.from(pregunta['opciones'] ?? []);

    return Scaffold(
      appBar: AppBar(
        title: Text('${indice + 1}/${preguntas.length}'),
        backgroundColor: const Color(0xFF1565C0),
        foregroundColor: Colors.white,
        actions: [Padding(padding: const EdgeInsets.all(8), child: Center(child: Text('$puntuacion pts', style: const TextStyle(color: Colors.white, fontSize: 16))))],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 20),
            Card(
              color: const Color(0xFF1565C0),
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Text(pregunta['enunciado'], style: const TextStyle(fontSize: 18, color: Colors.white, fontWeight: FontWeight.bold), textAlign: TextAlign.center),
              ),
            ),
            const SizedBox(height: 30),
            ...opciones.map((opcion) {
              Color color = Colors.white;
              if (respondida) {
                if (opcion == pregunta['respuesta_correcta']) color = Colors.green.shade100;
                else if (opcion == seleccionada) color = Colors.red.shade100;
              }
              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: ElevatedButton(
                  onPressed: () => responder(opcion),
                  style: ElevatedButton.styleFrom(backgroundColor: color, padding: const EdgeInsets.all(16)),
                  child: Text(opcion, style: const TextStyle(fontSize: 16, color: Colors.black87)),
                ),
              );
            }),
          ],
        ),
      ),
    );
  }
}

// ─── ADIVINA EL JUGADOR ───────────────────────────────────────────────────────

class PantallaAdivinaJugador extends StatefulWidget {
  const PantallaAdivinaJugador({super.key});

  @override
  State<PantallaAdivinaJugador> createState() => _PantallaAdivinaJugadorState();
}

class _PantallaAdivinaJugadorState extends State<PantallaAdivinaJugador> {
  List preguntas = [];
  int indice = 0;
  int puntuacion = 0;
  bool cargando = true;
  int pistaMostrada = 1;
  bool respondida = false;
  String? respuestaUsuario;
  final TextEditingController _controller = TextEditingController();

  @override
  void initState() {
    super.initState();
    cargarPreguntas();
  }

  Future<void> cargarPreguntas() async {
    final response = await http.get(Uri.parse('http://localhost:8000/preguntas/adivina-jugador?limite=10'));
    if (response.statusCode == 200) {
      setState(() {
        preguntas = json.decode(response.body);
        cargando = false;
      });
    }
  }

  void mostrarSiguientePista() {
    final pistas = List<String>.from(preguntas[indice]['pistas'] ?? []);
    if (pistaMostrada < pistas.length) {
      setState(() => pistaMostrada++);
    }
  }

  void comprobarRespuesta() {
    final correcta = preguntas[indice]['respuesta_correcta'].toString().toLowerCase();
    final usuario = _controller.text.toLowerCase().trim();
    setState(() {
      respondida = true;
      respuestaUsuario = _controller.text;
      if (usuario == correcta || correcta.contains(usuario) || usuario.contains(correcta.split(' ').last.toLowerCase())) {
        puntuacion += (5 - pistaMostrada + 1).clamp(1, 4) * 5;
      }
    });

    Future.delayed(const Duration(seconds: 2), () {
      if (indice < preguntas.length - 1) {
        setState(() { indice++; pistaMostrada = 1; respondida = false; respuestaUsuario = null; _controller.clear(); });
      } else {
        Navigator.pushReplacement(context, MaterialPageRoute(
          builder: (_) => PantallaResultado(puntuacion: puntuacion, total: preguntas.length * 20, titulo: 'Adivina el Jugador'),
        ));
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    if (cargando) return const Scaffold(body: Center(child: CircularProgressIndicator()));
    if (preguntas.isEmpty) return const Scaffold(body: Center(child: Text('No hay preguntas')));

    final pregunta = preguntas[indice];
    final pistas = List<String>.from(pregunta['pistas'] ?? []);
    final correcta = pregunta['respuesta_correcta'];

    return Scaffold(
      appBar: AppBar(
        title: Text('${indice + 1}/${preguntas.length}'),
        backgroundColor: const Color(0xFF6A1B9A),
        foregroundColor: Colors.white,
        actions: [Padding(padding: const EdgeInsets.all(8), child: Center(child: Text('$puntuacion pts', style: const TextStyle(color: Colors.white, fontSize: 16))))],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 10),
            const Text('¿Quién es este jugador?', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold), textAlign: TextAlign.center),
            const SizedBox(height: 20),
            ...List.generate(pistaMostrada, (i) => Card(
              color: const Color(0xFF6A1B9A),
              margin: const EdgeInsets.only(bottom: 8),
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Row(children: [
                  Text('Pista ${i + 1}: ', style: const TextStyle(color: Colors.white70, fontWeight: FontWeight.bold)),
                  Expanded(child: Text(pistas[i], style: const TextStyle(color: Colors.white, fontSize: 16))),
                ]),
              ),
            )),
            const SizedBox(height: 20),
            if (!respondida) ...[
              TextField(
                controller: _controller,
                decoration: const InputDecoration(
                  labelText: 'Escribe el nombre del jugador',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              Row(children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: comprobarRespuesta,
                    style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF6A1B9A), foregroundColor: Colors.white, padding: const EdgeInsets.all(14)),
                    child: const Text('Responder', style: TextStyle(fontSize: 16)),
                  ),
                ),
                if (pistaMostrada < pistas.length) ...[
                  const SizedBox(width: 10),
                  ElevatedButton(
                    onPressed: mostrarSiguientePista,
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.orange, foregroundColor: Colors.white, padding: const EdgeInsets.all(14)),
                    child: const Text('Pista', style: TextStyle(fontSize: 16)),
                  ),
                ],
              ]),
            ] else ...[
              Card(
                color: respuestaUsuario?.toLowerCase() == correcta.toLowerCase() ? Colors.green.shade100 : Colors.red.shade100,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(children: [
                    Text(
                      respuestaUsuario?.toLowerCase() == correcta.toLowerCase() ? '¡Correcto!' : 'Incorrecto',
                      style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold,
                          color: respuestaUsuario?.toLowerCase() == correcta.toLowerCase() ? Colors.green : Colors.red),
                    ),
                    Text('La respuesta era: $correcta', style: const TextStyle(fontSize: 16)),
                  ]),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

// ─── ADIVINA EL ESCUDO ────────────────────────────────────────────────────────

class PantallaAdivinaEscudo extends StatefulWidget {
  const PantallaAdivinaEscudo({super.key});

  @override
  State<PantallaAdivinaEscudo> createState() => _PantallaAdivinaEscudoState();
}

class _PantallaAdivinaEscudoState extends State<PantallaAdivinaEscudo> {
  List equipos = [];
  int indice = 0;
  int puntuacion = 0;
  bool cargando = true;
  String? seleccionada;
  bool respondida = false;
  late List<String> opciones;

  @override
  void initState() {
    super.initState();
    cargarEscudos();
  }

  Future<void> cargarEscudos() async {
    final response = await http.get(Uri.parse('http://localhost:8000/escudos?limite=20'));
    if (response.statusCode == 200) {
      final data = json.decode(response.body) as List;
      data.shuffle();
      setState(() {
        equipos = data.take(10).toList();
        cargando = false;
        generarOpciones();
      });
    }
  }

  void generarOpciones() {
    final correcto = equipos[indice]['nombre'];
    final todos = equipos.map((e) => e['nombre'] as String).toList();
    todos.remove(correcto);
    todos.shuffle();
    opciones = [correcto, ...todos.take(3)]..shuffle();
  }

  void responder(String opcion) {
    if (respondida) return;
    setState(() {
      seleccionada = opcion;
      respondida = true;
      if (opcion == equipos[indice]['nombre']) puntuacion += 10;
    });
    Future.delayed(const Duration(seconds: 2), () {
      if (indice < equipos.length - 1) {
        setState(() { indice++; seleccionada = null; respondida = false; generarOpciones(); });
      } else {
        Navigator.pushReplacement(context, MaterialPageRoute(
          builder: (_) => PantallaResultado(puntuacion: puntuacion, total: equipos.length * 10, titulo: 'Adivina el Escudo'),
        ));
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    if (cargando) return const Scaffold(body: Center(child: CircularProgressIndicator()));
    if (equipos.isEmpty) return const Scaffold(body: Center(child: Text('No hay escudos disponibles')));

    final equipo = equipos[indice];

    return Scaffold(
      appBar: AppBar(
        title: Text('${indice + 1}/${equipos.length}'),
        backgroundColor: const Color(0xFFE65100),
        foregroundColor: Colors.white,
        actions: [Padding(padding: const EdgeInsets.all(8), child: Center(child: Text('$puntuacion pts', style: const TextStyle(color: Colors.white, fontSize: 16))))],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 20),
            const Text('¿De qué equipo es este escudo?', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold), textAlign: TextAlign.center),
            const SizedBox(height: 30),
            Center(
              child: Container(
                width: 150,
                height: 150,
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Image.network(
                  equipo['escudo_url'],
                  fit: BoxFit.contain,
                  errorBuilder: (_, __, ___) => const Icon(Icons.shield, size: 80, color: Colors.grey),
                ),
              ),
            ),
            const SizedBox(height: 30),
            ...opciones.map((opcion) {
              Color color = Colors.white;
              if (respondida) {
                if (opcion == equipo['nombre']) color = Colors.green.shade100;
                else if (opcion == seleccionada) color = Colors.red.shade100;
              }
              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: ElevatedButton(
                  onPressed: () => responder(opcion),
                  style: ElevatedButton.styleFrom(backgroundColor: color, padding: const EdgeInsets.all(16)),
                  child: Text(opcion, style: const TextStyle(fontSize: 16, color: Colors.black87)),
                ),
              );
            }),
          ],
        ),
      ),
    );
  }
}

// ─── RESULTADO ────────────────────────────────────────────────────────────────

class PantallaResultado extends StatelessWidget {
  final int puntuacion;
  final int total;
  final String titulo;
  const PantallaResultado({super.key, required this.puntuacion, required this.total, required this.titulo});

  @override
  Widget build(BuildContext context) {
    final porcentaje = total > 0 ? (puntuacion / total * 100).round() : 0;
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.emoji_events, size: 100, color: Colors.amber),
            const SizedBox(height: 20),
            Text('¡$titulo completado!', style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            const SizedBox(height: 10),
            Text('$puntuacion / $total puntos', style: const TextStyle(fontSize: 28, color: Color(0xFF1B5E20), fontWeight: FontWeight.bold)),
            const SizedBox(height: 5),
            Text('$porcentaje% de acierto', style: const TextStyle(fontSize: 18, color: Colors.grey)),
            const SizedBox(height: 40),
            ElevatedButton(
              onPressed: () => Navigator.popUntil(context, (route) => route.isFirst),
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF1B5E20), foregroundColor: Colors.white, padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 15)),
              child: const Text('Volver al inicio', style: TextStyle(fontSize: 18)),
            ),
          ],
        ),
      ),
    );
  }
}