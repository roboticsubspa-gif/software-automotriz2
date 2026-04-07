--
-- PostgreSQL database dump
--


-- Dumped from database version 16.10
-- Dumped by pg_dump version 16.10

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: cliente; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cliente (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    telefono character varying(50)
);


ALTER TABLE public.cliente OWNER TO postgres;

--
-- Name: cliente_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cliente_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cliente_id_seq OWNER TO postgres;

--
-- Name: cliente_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cliente_id_seq OWNED BY public.cliente.id;


--
-- Name: cotizacion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cotizacion (
    id integer NOT NULL,
    numero character varying(50),
    cliente character varying(200),
    rut character varying(50),
    contacto character varying(100),
    fecha_documento date,
    fecha_vencimiento date,
    descripcion text,
    cantidad integer,
    valor double precision,
    neto double precision,
    iva double precision,
    total double precision
);


ALTER TABLE public.cotizacion OWNER TO postgres;

--
-- Name: cotizacion_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cotizacion_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cotizacion_id_seq OWNER TO postgres;

--
-- Name: cotizacion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cotizacion_id_seq OWNED BY public.cotizacion.id;


--
-- Name: gasto_st; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gasto_st (
    id integer NOT NULL,
    fecha timestamp without time zone,
    descripcion character varying(500) NOT NULL,
    costo double precision
);


ALTER TABLE public.gasto_st OWNER TO postgres;

--
-- Name: gasto_st_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.gasto_st_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.gasto_st_id_seq OWNER TO postgres;

--
-- Name: gasto_st_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.gasto_st_id_seq OWNED BY public.gasto_st.id;


--
-- Name: ot; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ot (
    id integer NOT NULL,
    numero character varying(50) NOT NULL,
    vehiculo_id integer NOT NULL,
    fecha_creacion timestamp without time zone,
    descripcion_trabajo text NOT NULL,
    observaciones text,
    costo_estimado double precision,
    estado character varying(30),
    tipo_ot character varying(20),
    foto bytea,
    foto_mime character varying(80)
);


ALTER TABLE public.ot OWNER TO postgres;

--
-- Name: ot_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ot_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ot_id_seq OWNER TO postgres;

--
-- Name: ot_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ot_id_seq OWNED BY public.ot.id;


--
-- Name: repuesto; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.repuesto (
    id integer NOT NULL,
    codigo character varying(50) NOT NULL,
    nombre character varying(120) NOT NULL,
    stock integer NOT NULL,
    precio double precision NOT NULL
);


ALTER TABLE public.repuesto OWNER TO postgres;

--
-- Name: repuesto_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.repuesto_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.repuesto_id_seq OWNER TO postgres;

--
-- Name: repuesto_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.repuesto_id_seq OWNED BY public.repuesto.id;


--
-- Name: repuesto_usado; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.repuesto_usado (
    id integer NOT NULL,
    ot_id integer NOT NULL,
    repuesto_id integer NOT NULL,
    cantidad integer NOT NULL
);


ALTER TABLE public.repuesto_usado OWNER TO postgres;

--
-- Name: repuesto_usado_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.repuesto_usado_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.repuesto_usado_id_seq OWNER TO postgres;

--
-- Name: repuesto_usado_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.repuesto_usado_id_seq OWNED BY public.repuesto_usado.id;


--
-- Name: servicio; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.servicio (
    id integer NOT NULL,
    vehiculo_id integer NOT NULL,
    fecha timestamp without time zone,
    descripcion text NOT NULL,
    costo double precision
);


ALTER TABLE public.servicio OWNER TO postgres;

--
-- Name: servicio_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.servicio_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.servicio_id_seq OWNER TO postgres;

--
-- Name: servicio_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.servicio_id_seq OWNED BY public.servicio.id;


--
-- Name: tarea; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tarea (
    id integer NOT NULL,
    fecha_creacion timestamp without time zone,
    titulo text NOT NULL,
    detalle text,
    estado character varying(30),
    prioridad character varying(20),
    responsable character varying(80),
    vencimiento date
);


ALTER TABLE public.tarea OWNER TO postgres;

--
-- Name: tarea_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tarea_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tarea_id_seq OWNER TO postgres;

--
-- Name: tarea_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tarea_id_seq OWNED BY public.tarea.id;


--
-- Name: toma_hora; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.toma_hora (
    id integer NOT NULL,
    fecha_creacion timestamp without time zone,
    fecha date NOT NULL,
    responsable character varying(80),
    actividad character varying(200) NOT NULL,
    detalle text,
    horas double precision NOT NULL,
    estado character varying(30),
    urgencia character varying(20),
    rapidez character varying(30)
);


ALTER TABLE public.toma_hora OWNER TO postgres;

--
-- Name: toma_hora_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.toma_hora_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.toma_hora_id_seq OWNER TO postgres;

--
-- Name: toma_hora_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.toma_hora_id_seq OWNED BY public.toma_hora.id;


--
-- Name: usuario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuario (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    password_hash text NOT NULL,
    rol character varying(20)
);


ALTER TABLE public.usuario OWNER TO postgres;

--
-- Name: usuario_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuario_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuario_id_seq OWNER TO postgres;

--
-- Name: usuario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuario_id_seq OWNED BY public.usuario.id;


--
-- Name: vehiculo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vehiculo (
    id integer NOT NULL,
    patente character varying(20) NOT NULL,
    modelo character varying(100),
    cliente_id integer NOT NULL,
    foto bytea,
    foto_mime character varying(80)
);


ALTER TABLE public.vehiculo OWNER TO postgres;

--
-- Name: vehiculo_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vehiculo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehiculo_id_seq OWNER TO postgres;

--
-- Name: vehiculo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vehiculo_id_seq OWNED BY public.vehiculo.id;


--
-- Name: cliente id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cliente ALTER COLUMN id SET DEFAULT nextval('public.cliente_id_seq'::regclass);


--
-- Name: cotizacion id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cotizacion ALTER COLUMN id SET DEFAULT nextval('public.cotizacion_id_seq'::regclass);


--
-- Name: gasto_st id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gasto_st ALTER COLUMN id SET DEFAULT nextval('public.gasto_st_id_seq'::regclass);


--
-- Name: ot id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ot ALTER COLUMN id SET DEFAULT nextval('public.ot_id_seq'::regclass);


--
-- Name: repuesto id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repuesto ALTER COLUMN id SET DEFAULT nextval('public.repuesto_id_seq'::regclass);


--
-- Name: repuesto_usado id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repuesto_usado ALTER COLUMN id SET DEFAULT nextval('public.repuesto_usado_id_seq'::regclass);


--
-- Name: servicio id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.servicio ALTER COLUMN id SET DEFAULT nextval('public.servicio_id_seq'::regclass);


--
-- Name: tarea id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tarea ALTER COLUMN id SET DEFAULT nextval('public.tarea_id_seq'::regclass);


--
-- Name: toma_hora id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.toma_hora ALTER COLUMN id SET DEFAULT nextval('public.toma_hora_id_seq'::regclass);


--
-- Name: usuario id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario ALTER COLUMN id SET DEFAULT nextval('public.usuario_id_seq'::regclass);


--
-- Name: vehiculo id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehiculo ALTER COLUMN id SET DEFAULT nextval('public.vehiculo_id_seq'::regclass);


--
-- Data for Name: cliente; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cliente (id, nombre, telefono) FROM stdin;
8	Egaña automotriz	976034758
9	ERWIN MENA	994614806
11	ALEJANDRA MICHIELI	949896183
12	EGAÑA CONSIGNADOS	
13	Pedro Stangue	986637677
14	Maximiliano Pacheco	990871663
15	FERNANDO GARCIA	972142884
16	PH motors	+56 9 7103 3864
17	Pablo Barraza	976542892
18	MARCELA ANDRADE	994485912
19	MARTIN BARRIA	+56 9 7242 7529
20	Matias Perez	986412669
21	DANIEL RIVERA	946519664
22	Mauricio	9888564
23	CARLA VALENTINA BUSTAMANTE FUENTES	97723440
24	Camilo dattoli	993079573
25	Nicole de la peña	966555115
26	FRANCISCO ARRIAGADA	957649396
27	Cesar lillo	965924267
28	MARIA HERNANDEZ	975320338
29	YAGAN CHILE	998492616
30	Nicole Montenegro	998471040
31	FRAMCISCO OLABARRIA	983853759
32	Gabriel veloso	949331818
33	Claudia harbasch	953305526
34	Francisco lillo	986637677
35	Pamela vargas	966831942
37	ALLISON HINRICHSEN	944071289
38	Pedro arroyo	972427529
39	Martín barria	
40	Martín barria	+56 9 7242 7529
41	nicolas barria	949798355
42	BENJAMIN CONTRERAS	930812976
43	Constanza	984385996
44	BENJAMIN SANZ	965676049
45	franco	959373948
46	MONICA VIVIAN MONTANDON PRIETO	
47	BANCO INTERNACIONAL	
48	Tomas Deomojan	
49	Pablo Andrés Espina	956918306
50	Henry Oporto	986304047
51	BELEN AROCA	934060527
\.


--
-- Data for Name: cotizacion; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cotizacion (id, numero, cliente, rut, contacto, fecha_documento, fecha_vencimiento, descripcion, cantidad, valor, neto, iva, total) FROM stdin;
14	14	ROCIO VARGAS	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
15	15	BERNANDO LUKASCHEWSKY SANHUEZA	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
16	16	CRISTOBAL ROSAS	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
\.


--
-- Data for Name: gasto_st; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gasto_st (id, fecha, descripcion, costo) FROM stdin;
1	2026-03-19 23:32:12.947716	2025-12-11 22:12:17.833332	\N
2	2026-03-19 23:32:12.948938	2025-12-12 15:34:54.925633	\N
\.


--
-- Data for Name: ot; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ot (id, numero, vehiculo_id, fecha_creacion, descripcion_trabajo, observaciones, costo_estimado, estado, tipo_ot, foto, foto_mime) FROM stdin;
3	OT-20251211-0001	4	2025-12-11 14:06:39.865294	Cambio de turbo	Reemplazo de turbo debido a falla en filtración de aceite por cetroshaft	100000	Abierta	externo	\N	\N
2	OT-20251210-0002	3	2025-12-10 15:42:50.668897	REEMPLAZO DE EMPAQUETADURA DE TAPA DE VALVULAS, CAMBIO DE RIEL DE RETORNO INYECTORES Y REEMPLAZO PAR DE BIELETAS DELANTERAS.	BIELETAS EN MUY MAL ESTADO, PERDIDA DE ACEITE POR TAPA DE VALVULAS Y PERDIDA DE COMBUSTIBLE POR RETORNOS DE INYECCION.\r\nCOSTOS: \r\nPAR BIELETAS= 18.000 EMPAQUETADURA= 20.000 RETORNOS= 9.000 HH= 120.000	167000	Abierta	externo	\N	\N
4	OT-20251211-0002	12	2025-12-11 14:48:23.876457	Falla en Funcionamiento de Hazard e intermitentes, limpia parabrisas check engine encendido		50000	Abierta	externo	\N	\N
5	OT-20251211-0003	13	2025-12-11 17:05:53.832444	INFORMES MES DE DICIEMBRE 2025	INFOMES VEHICULARES DICIEMBRE 2025	800000	Abierta	externo	\N	\N
6	OT-20251211-0004	25	2025-12-11 19:15:20.639387	DESTAPADO Y CAMBIO DE INYECTORES, ELIMINACION DPF Y REVISION SIESTEMA DE ESACPE.	CAMIONETA MUY SATURADA EN HOLLIN Y PETROLEO CRUDO, INYECTOR FISURADO	340000	Abierta	externo	\N	\N
7	OT-20251212-0001	29	2025-12-12 15:21:43.115965	Desarme y arme para cambio de rodamiento viscoso	El trabajo fue realizado pero fallo rodamiento debido a mala reparación por parte del cliente, se vuleve a enviar para corregir falla y nuevamente se realizo de mala forma, debido a esto se procede a realizar entrega del vehículo con ruido ya que cliente no logra realizar reparación solicitada.	150000	Abierta	externo	\N	\N
8	OT-20251212-0002	25	2025-12-12 15:28:45.918652	Cambio de aceite, filtro aceite y cambio filtro de petroleo.	vehículo fue anteriormente reparado de inyectores, por lo que el aceite estaba muy sucio, ademas filtro de petroleo estaba muy saturado, lo cual explica la falla de los inyectores.	103000	Abierta	externo	\N	\N
9	OT-20251213-0001	22	2025-12-13 20:57:02.069352	Reemplazo de birlos y tuercas de rueda	se realizo reemplazo de birlos por lo que se desarmaron masas completas y tambores..	40000	Abierta	externo	\N	\N
10	OT-20251230-0001	62	2025-12-30 00:28:52.754844	CAMBIO DE ACEITE Y FILTRO	CLIENTE FACILITA INSUMOS	20000	Abierta	externo	\N	\N
11	OT-20251230-0002	58	2025-12-30 00:32:32.884018	CAMBIO DE PICKUP COMPLETO Y REPARACION PARACHOQUE TRASERO.	CAMIONETA CONSIGNADA SUFRIO UN ACCIDENTE.	70000	Abierta	externo	\N	\N
12	OT-20251230-0003	63	2025-12-30 00:35:48.36261	CAMBIO DE ESPEJO RETROVISOR	CLIENTE TRAE EL REPUESTO	30000	Abierta	externo	\N	\N
13	OT-20251230-0004	64	2025-12-30 00:42:48.248141	CAMBIO DE BUJIAS Y BOBINAS	CLIENTE TRAE LOS REPUESTOS	20000	Abierta	externo	\N	\N
14	OT-20251230-0005	65	2025-12-30 00:48:12.504845	REPARACION MOTOR LIMPIA PARABRISAS	SE REALIZO REPARACION ELECTRICA Y MECANICA A SISTEMA DE LIMPIA PARBRISAS	30000	Abierta	externo	\N	\N
15	OT-20251230-0006	5	2025-12-30 00:50:33.885342	REPARACION SISTEMA LIMPIA PARABRISAS	CAMBIO DE MANGUERAS LIMPIA PARABRISAS	10000	Abierta	externo	\N	\N
16	OT-20251230-0007	66	2025-12-30 13:06:55.251555	Instalación de pisaderas y barra antivuelco	Se realiza instalación de accesorios a Toyota SR	600000	Abierta	externo	\N	\N
17	OT-20260102-0001	80	2026-01-02 16:41:09.696393	CAMBIO PASTILLAS DE FRENO DELANTERAS.	PASTILLAS CON POCA VIDA UTIL.	30000	Abierta	externo	\N	\N
18	OT-20260107-0001	91	2026-01-07 15:34:57.243862	LIMPIEZA COMPLETA DE CIRCULACION DEL AGUA, INSTALACION SENSOR DE TEMPERATURA PARA ELECTRO VENTILADOR, CAMBIO DE LIQUIDO REFRIGERANTE, REEMPLAZO DE ACEITE Y FILTRO, MANTENCION Y CAMBIO DE PASTILLAS DELANTERAS.	El vehículo ingresa al taller debido a un sobrecalentamiento del motor. Se procede al reemplazo del termostato, a la limpieza y destape de las cañerías del sistema de refrigeración, y a la instalación del sensor de temperatura con el fin de restablecer el funcionamiento del electroventilador. Adicionalmente, el cliente informa una falla en las pastillas de freno.	90000	Abierta	externo	\N	\N
19	OT-20260109-0001	63	2026-01-09 21:44:16.34804	instalación retrovisor derecho	cliente ingresa para instalación de retrovisor derecho, el cual no retornaba de forma automática.	15000	Abierta	externo	\N	\N
20	OT-20260110-0001	80	2026-01-10 13:43:01.9959	Cambio de aceite y filtro\r\ncambio ampolleta h8	cliente retorna para cambio de aceite, filtro y luz en mal estado	85000	Abierta	externo	\N	\N
21	OT-20260110-0002	13	2026-01-10 13:47:00.996961	informes mensuales egaña.	Egaña automotriz solicita informes y revisiones completas de vehículos.	800000	Abierta	externo	\N	\N
22	OT-20260114-0001	60	2026-01-14 21:15:47.008127	cambio de aceite, reparación electro, instalación bulbo temperatura	vehiculó sin funcionamiento de electroventilador, pequeña fuga de aceite en reten de cigüeñal delantero	77000	Abierta	externo	\N	\N
23	OT-20260115-0001	111	2026-01-15 12:31:50.739698	CARGA DE A/C	VEHICULO INGRESA CON BAJO NIVEL DE A/C	20000	Abierta	externo	\N	\N
24	OT-20260115-0002	112	2026-01-15 15:25:54.773063	VETNTA DE ACEITE MOBIL ONE	CLIENTE COMPRA ACEITE PARA RELLENAR SU CAMIONETA	65000	Abierta	externo	\N	\N
25	OT-20260115-0003	114	2026-01-15 22:00:33.461727	Mantenimiento completo	Cliente paga en efectivo.	204000	Abierta	externo	\N	\N
26	OT-20260117-0001	116	2026-01-17 13:58:04.889758	CAMBIO DE ACEITE Y BUTACA PILOTO		200000	Abierta	externo	\N	\N
27	OT-20260120-0001	121	2026-01-20 21:35:23.952775	cambio de aceite, alineación, reapriete tren delantero, cambio de pastillas delanteras, espejo retrovisor izquierdo, moldura exterior puerta trasera	vehículo solo con detalles estéticos.	245000	Cerrada	externo	\N	\N
28	OT-20260121-0001	36	2026-01-21 21:05:48.179538	cambio de kit de embrague	vehículo ingresa a taller por ruido en caja de cambios, por lo cuál se procede a diagnosticar fallo en volante de inercia	1050000	Abierta	externo	\N	\N
29	OT-20260122-0001	127	2026-01-22 15:31:06.188487	REVISION DE TREN DELANTERO, CAMBIO DE PASTILLAS DELANTERAS.	CLIENTE INGRESA POR RUIDO EN TREN DELANTERO, SE REVISA Y SE ENCUETRA MASA DE RUEDA IZQUIERA SUELTA, SE PROCEDE A REAPRETAR.\r\nCLIENTE PAGA EN EFECETIVO	60000	Abierta	externo	\N	\N
30	OT-20260203-0001	36	2026-02-03 15:28:27.952852	cambio de correa de distribución	cliente solicita cambio por prevencion	175000	Abierta	externo	\N	\N
31	OT-20260203-0002	38	2026-02-03 15:30:44.10792	cambio amortiguadores traseros	cambio par de amortiguadores	28000	Abierta	externo	\N	\N
32	OT-20260203-0003	78	2026-02-03 15:34:04.604011	cambio de motor vidrio trasero	motor quemado	80000	Abierta	externo	\N	\N
33	OT-20260203-0004	146	2026-02-03 16:32:01.422301	Mantenimiento completo	se realizo cambio de filtro de aire, filtro de combustible, filtro de aceite y filtro de polen, además se realizo cambio de aceite	230000	Abierta	externo	\N	\N
34	OT-20260203-0005	120	2026-02-03 16:37:25.935329	mantenimiento tren delantero y trasero, además se realizo carga de aire acondicionado	camioneta ingresa con pastillas nuevas, las cuales fueron instaladas de forma invertida.	510000	Abierta	externo	\N	\N
35	OT-20260204-0001	147	2026-02-04 15:17:56.490062	CAMBIO DE PASTILLAS DELANTERAS Y REVISION GENERAL	PASTILLAS DE FRENO SE ENCONTRABAN CRISTALIZADAS. ADEMAS SE ENCONTRO BIELETAS DESGASTADAS Y PEQUEÑA FUGA DE ACEITE POR RETEN DE CIGUEÑAL.	50000	Abierta	externo	\N	\N
36	OT-20260216-0001	148	2026-02-16 20:20:53.71321	Vehículo ingresa por fuelle de triceta y fuelle de dirección en mal estado, por lo cual se procede a realizar engrase y cambio de ambos fuelles, además se vuelve a montar y engrasar fuelle de dirección lado derecho.	vehículo se encontraba con un fuelle desmontado y dos en mal estado	77500	Abierta	externo	\N	\N
37	OT-20260220-0001	149	2026-02-20 15:32:47.062577	CAMBIO DE ACEITE, FILTRO Y PINTADO DE LLANTAS		98000	Abierta	externo	\N	\N
38	OT-20260220-0002	150	2026-02-20 16:18:36.909791	CAMBIO DE CULATIN, TAQUES HIDRAULICOS, CAMBIO DE ACEITE, CAMBIO DE EMPAQUETADURA DE VALVULAS, CAMBIODE SOPORTES DE ARBOL DE LEVAS Y CAMBIO DE BALATAS INTERNAS	FUGA POR TAPA DE VALVULAS, TAQUES HIDRAULICOS ROTOS, SOPORTES DE LEVAS QUEBRADOS Y ACEITE MUY BAJO Y SIN VISCOSIDAD.\r\nBALATAS INTERNAS MUY DESGASTADAS FRENO DE MANO NO OPERATIVO.	541000	Abierta	externo	\N	\N
39	OT-20260220-0003	8	2026-02-20 16:20:04.603622	CAMBIO DE ESPEJO RETROVISOR PILOTO	ESPEJO QUEBRADO.	140000	Abierta	externo	\N	\N
40	OT-20260220-0004	124	2026-02-20 16:21:13.567133	SE REALIZO EL PEGADO DE ESPEJO RETROVISOR INTERNO.		10000	Abierta	externo	\N	\N
41	OT-20260220-0005	31	2026-02-20 16:22:27.096667	SE REEMPLAZO MODULO DE VELOCIDAD CRUCERO	\N	70000	Abierta	externo	\N	\N
42	OT-20260220-0006	88	2026-02-20 16:23:29.922816	CAMBIO DE BOMBA DE AGUA, CAMBIO DE RADIADOR DE CALEFACCION	\N	102219	Abierta	externo	\N	\N
43	OT-20260220-0007	152	2026-02-20 17:55:45.133359	CAMBIO DE ACEITE	CLIENTE TRAE LOS INSUMNOS	15000	Abierta	externo	\N	\N
44	OT-20260220-0008	104	2026-02-20 18:02:24.265663	CAMBIO DE ACEITE Y FILTRO		100000	Abierta	externo	\N	\N
45	OT-20260220-0009	153	2026-02-20 18:04:00.866396	CAMBIO DE SOPORTE DE MOTOR, REAPRIETE TREN DELANTERO		75000	Abierta	externo	\N	\N
46	OT-20260220-0010	154	2026-02-20 18:07:14.500572	CAMBIO DE BIELETAS DELANTERAS	BIELETAS EN MAL ESTADO	30000	Abierta	externo	\N	\N
47	OT-20260220-0011	30	2026-02-20 18:18:35.744482	CAMBIO DE LIQUIDO REFRIGERANTE, CAMBIO DE ACEITE, CAMBIO DE PASTILLAS.	VEHICULO CON PASTILLAS MUY DESGASTADAS, ACEITE CON BAJA VISCOSIDAD Y LIQUIDO REFRIGERANTE CORTADO.	80000	Abierta	externo	\N	\N
48	OT-20260220-0012	155	2026-02-20 18:28:10.906569	REPARACION GENERAL DE FRONTAL		289300	Abierta	externo	\N	\N
49	OT-20260220-0013	156	2026-02-20 21:19:18.033554	CAMBIO DE ACEITE Y FILTRO	SIN REGISTRO DE MANTENCIONES	95000	Abierta	externo	\N	\N
50	OT-20260223-0001	38	2026-02-23 20:18:41.089637	cambio de aceite y filtro		50000	Abierta	externo	\N	\N
51	OT-20260223-0002	157	2026-02-23 20:27:36.966641	CAMBIO DE ACEITE, FILTRO, LIQUIDO REFRIGERANTE		110000	Abierta	externo	\N	\N
52	OT-20260224-0001	158	2026-02-24 13:14:44.129342	CAMBIO DE ACEITE Y FILTRO	VEHICULO CON CORREA HUMEDA, AUN EN BUEN ESTADO	50000	Abierta	externo	\N	\N
53	OT-20260224-0002	159	2026-02-24 20:23:11.547789	cambio de aceite	cambio de aceite y filtro	100000	Abierta	externo	\N	\N
54	OT-20260225-0001	160	2026-02-25 18:10:36.354296	Cambio de aceite, filtro y revisión tecnica.	Muy buen estado general, correa con muestras de desgaste, se encontraron micro restos de goma en el cambio.\r\nSe recomienda cambio de correa a los 40.000km	93450	Abierta	externo	\N	\N
55	OT-20260225-0002	58	2026-02-25 21:58:47.499308	REEMPLAZO DE BATERIA	BATERIA SE ENCONTRABA EN MAL ESTADO.	80000	Abierta	externo	\N	\N
56	OT-20260227-0001	13	2026-02-27 20:27:14.473078	informes mensuales		800000	Abierta	externo	\N	\N
57	OT-20260227-0002	166	2026-02-27 20:47:50.186543	CAMBIO DE ACEITE Y FILTRO	ACEITE SE NOTO FUERA DE NORMA,(COLORACION MUY OSCURA)	70000	Abierta	externo	\N	\N
58	OT-20260302-0001	167	2026-03-02 13:17:08.061965	CAMBIO DE SOPORTE DE MOTOR	SOPORTE SE ENCONTRABA CON BUJE CORTADO.	55000	Abierta	externo	\N	\N
59	OT-20260304-0001	114	2026-03-04 20:18:23.032717	Reapriete de masas delanteras.	vehículo con defectos en bandejas, terminales, rotulas y discos; se recomienda reemplazar tren delantero.	10000	Abierta	externo	\N	\N
60	OT-20260304-0002	152	2026-03-04 22:36:11.779595	CAMBIO DE ACEITE	CLIENTE TRAE LOS REPUESTOS	15000	Abierta	externo	\N	\N
61	OT-20260305-0001	50	2026-03-05 15:34:40.275468	CAMBIO DE PASTILLAS DE FRENO	CLIENTE TRAE REPUESTOS.	10000	Abierta	externo	\N	\N
62	OT-20260306-0001	68	2026-03-06 18:48:24.737084	Cambio de aceite y filtro		52500	Abierta	externo	\N	\N
63	OT-20260311-0001	189	2026-03-11 20:54:05.199779	LIMPIEZA GENERAL DE ADMISION, CAMBIO DE ECEITE Y FILTRO, TAPADO VALVULA EGR.	MUCHA CAPA DE HOLLIN EN ADMISION	184000	Abierta	externo	\N	\N
64	OT-20260312-0001	190	2026-03-12 14:42:57.160352	Cambio de kit de embrague y cambio de aceite caja manual.	Vehículo se encontraba con embrague muy desgastado y nivel de aceite de caja muy bajo	160000	Abierta	externo	\N	\N
65	OT-20260316-0001	191	2026-03-16 18:12:51.161793	REVISION Y USO DE SCANNER	SE ENCONTRO APERTURA DE CJA DE CAMBIO VEHICULO DE EMPRESA	25000	Abierta	externo	\N	\N
\.


--
-- Data for Name: repuesto; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.repuesto (id, codigo, nombre, stock, precio) FROM stdin;
1	3	destornillador de paleta	5	4
2	destornillador cruz	destornillador cruz	3	0
3	multi puntas	multi puntas	4	0
4	lima	lima	1	0
5	alicate punta	alicate punta	1	0
6	alicate plano	alicate plano	1	0
7	alicate cortante	alicate cortante	1	0
8	alicate plano chico	alicate plano chico	1	0
9	extractor de abrazaderas	extractor de abrazaderas	1	0
10	compresimetro	compresimetro	1	0
12	caja de dados para sensores de oxigeno	maleta de dados impacto	1	0
13	caja de dados de impacto	maleta con dados mixtos	1	0
14	pistola de pintura	pistola de pintura	2	0
15	caja de golillas	maleta de golillas	1	0
16	maleta de juego de orrines universales	maleta de juego de orrines universales	1	0
17	galletera	galletera	1	0
18	chicharras buenas	chicharras buenas	3	0
19	chicharras malas	chicharras malas	2	0
20	pistola de impacto	pistola de impacto	1	0
21	scanner	scanner	2	0
22	caja de dados (incompleta)	caja de dados (incompleta)	2	0
23	cargador de bateria	cargador de bateria	2	0
24	caiman	caiman	1	0
25	llave regulable	llave regulable	1	0
26	martillo normal	martillo	1	0
27	martillo de goma	martillo de goma	1	0
28	pela cable	pela cables	1	0
29	araña saca filtros	araña saca filtros	1	0
30	maquina de soldar	maquina de soldar	1	0
31	barrote de fuerza	barrote de fuerza	1	0
32	gata	gata	1	0
33	soplete	soplete	1	0
34	pistola neumatica	pistola neumatica	1	0
35	pistola de aceite	pistola de presión limpieza	1	0
36	extractor de filtros de aceite	correa extractor de filtros de aceite	1	0
37	llave de torque	llave de torque	1	0
38	paquete de llaves allen	paquete de llaves allen	1	0
39	pie de metro	pie de metro	1	0
11	comprimidor de frenos	maleta de dados para sensores de oxigeno	1	0
\.


--
-- Data for Name: repuesto_usado; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.repuesto_usado (id, ot_id, repuesto_id, cantidad) FROM stdin;
\.


--
-- Data for Name: servicio; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.servicio (id, vehiculo_id, fecha, descripcion, costo) FROM stdin;
1	7	2025-12-11 14:44:00.007713	2025-12-11 14:44:00.007713	10000
6	6	2025-12-11 15:14:19.551404	2025-12-11 15:14:19.551404	0
7	9	2025-12-11 15:15:18.124681	2025-12-11 15:15:18.124681	0
8	8	2025-12-11 15:16:23.760571	2025-12-11 15:16:23.760571	0
9	5	2025-12-11 15:18:09.562961	2025-12-11 15:18:09.562961	0
10	10	2025-12-11 15:19:40.38031	2025-12-11 15:19:40.380310	0
12	14	2025-12-11 15:23:27.675557	2025-12-11 15:23:27.675557	0
13	11	2025-12-11 15:26:40.217923	2025-12-11 15:26:40.217923	0
14	15	2025-12-11 15:29:17.004051	2025-12-11 15:29:17.004051	0
15	16	2025-12-11 15:31:12.910868	2025-12-11 15:31:12.910868	0
16	17	2025-12-11 15:38:35.372423	2025-12-11 15:38:35.372423	0
17	18	2025-12-11 15:39:26.977343	2025-12-11 15:39:26.977343	0
18	19	2025-12-11 15:47:58.643377	2025-12-11 15:47:58.643377	0
19	20	2025-12-11 15:48:53.149934	2025-12-11 15:48:53.149934	0
20	21	2025-12-11 15:49:47.109746	2025-12-11 15:49:47.109746	0
21	22	2025-12-11 15:50:27.868208	2025-12-11 15:50:27.868208	0
22	23	2025-12-11 15:51:00.336097	2025-12-11 15:51:00.336097	0
23	24	2025-12-11 15:56:57.988233	2025-12-11 15:56:57.988233	0
24	26	2025-12-11 22:15:38.000297	2025-12-11 22:15:38.000297	0
25	27	2025-12-11 22:17:24.551451	2025-12-11 22:17:24.551451	0
26	28	2025-12-11 22:19:52.016236	2025-12-11 22:19:52.016236	0
27	4	2025-12-12 20:53:14.535156	2025-12-12 20:53:14.535156	0
28	30	2025-12-12 20:55:35.636774	2025-12-12 20:55:35.636774	0
29	31	2025-12-12 20:59:52.40308	2025-12-12 20:59:52.403080	0
31	33	2025-12-13 21:02:50.323019	2025-12-13 21:02:50.323019	0
32	34	2025-12-16 13:32:44.968375	2025-12-16 13:32:44.968375	0
33	35	2025-12-16 13:34:57.670849	2025-12-16 13:34:57.670849	0
35	38	2025-12-17 13:53:33.526516	2025-12-17 13:53:33.526516	0
36	36	2025-12-17 14:14:08.480329	2025-12-17 14:14:08.480329	0
37	16	2025-12-17 16:13:16.33197	2025-12-17 16:13:16.331970	0
38	40	2025-12-17 16:16:17.130492	2025-12-17 16:16:17.130492	0
39	41	2025-12-29 23:36:22.292378	2025-12-29 23:36:22.292378	0
40	42	2025-12-29 23:37:12.736204	2025-12-29 23:37:12.736204	0
41	43	2025-12-29 23:38:16.663071	2025-12-29 23:38:16.663071	0
42	44	2025-12-29 23:39:56.641192	2025-12-29 23:39:56.641192	0
43	45	2025-12-29 23:56:45.098539	2025-12-29 23:56:45.098539	0
44	46	2025-12-29 23:57:48.395007	2025-12-29 23:57:48.395007	0
45	47	2025-12-29 23:59:49.948212	2025-12-29 23:59:49.948212	0
46	48	2025-12-30 00:00:50.126542	2025-12-30 00:00:50.126542	0
47	49	2025-12-30 00:01:28.618824	2025-12-30 00:01:28.618824	0
48	49	2025-12-30 00:01:33.5125	2025-12-30 00:01:33.512500	0
49	50	2025-12-30 00:02:41.651166	2025-12-30 00:02:41.651166	0
50	51	2025-12-30 00:03:17.682045	2025-12-30 00:03:17.682045	0
51	52	2025-12-30 00:04:34.61134	2025-12-30 00:04:34.611340	0
52	53	2025-12-30 00:05:42.99547	2025-12-30 00:05:42.995470	0
53	54	2025-12-30 00:06:24.516275	2025-12-30 00:06:24.516275	0
54	55	2025-12-30 00:11:00.544463	2025-12-30 00:11:00.544463	0
55	56	2025-12-30 00:11:58.754874	2025-12-30 00:11:58.754874	0
56	57	2025-12-30 00:12:43.263976	2025-12-30 00:12:43.263976	0
57	58	2025-12-30 00:13:14.079798	2025-12-30 00:13:14.079798	0
58	59	2025-12-30 00:19:08.874644	2025-12-30 00:19:08.874644	0
59	60	2025-12-30 00:19:34.681306	2025-12-30 00:19:34.681306	0
60	61	2025-12-30 00:20:53.463096	2025-12-30 00:20:53.463096	0
61	67	2025-12-30 16:07:39.002453	2025-12-30 16:07:39.002453	0
62	68	2025-12-30 16:08:07.146042	2025-12-30 16:08:07.146042	0
63	69	2025-12-30 16:08:39.478529	2025-12-30 16:08:39.478529	0
64	71	2025-12-30 16:09:19.02947	2025-12-30 16:09:19.029470	0
65	72	2025-12-30 16:09:55.092025	2025-12-30 16:09:55.092025	0
66	66	2025-12-30 16:10:19.996409	2025-12-30 16:10:19.996409	0
67	73	2025-12-30 16:14:28.196924	2025-12-30 16:14:28.196924	0
68	74	2025-12-30 16:15:23.706887	2025-12-30 16:15:23.706887	0
69	75	2025-12-30 16:16:13.616739	2025-12-30 16:16:13.616739	0
70	76	2025-12-31 00:07:58.930088	2025-12-31 00:07:58.930088	0
71	77	2025-12-31 00:09:15.799378	2025-12-31 00:09:15.799378	0
72	78	2025-12-31 00:10:38.297157	2025-12-31 00:10:38.297157	0
73	79	2025-12-31 00:11:11.541404	2025-12-31 00:11:11.541404	0
74	80	2025-12-31 00:12:41.140667	2025-12-31 00:12:41.140667	0
75	16	2026-01-02 13:46:09.451202	2026-01-02 13:46:09.451202	0
77	77	2026-01-06 17:10:20.398421	2026-01-06 17:10:20.398421	0
78	83	2026-01-06 17:14:34.785544	2026-01-06 17:14:34.785544	0
79	68	2026-01-06 21:19:24.495149	2026-01-06 21:19:24.495149	0
80	45	2026-01-06 21:24:20.453778	2026-01-06 21:24:20.453778	0
81	84	2026-01-06 22:06:06.232333	2026-01-06 22:06:06.232333	0
82	85	2026-01-06 22:08:00.971471	2026-01-06 22:08:00.971471	0
83	86	2026-01-06 22:10:53.463369	2026-01-06 22:10:53.463369	0
84	87	2026-01-06 22:12:19.997671	2026-01-06 22:12:19.997671	0
85	88	2026-01-06 22:13:37.09386	2026-01-06 22:13:37.093860	0
86	89	2026-01-06 22:17:55.461022	2026-01-06 22:17:55.461022	0
87	74	2026-01-06 22:18:40.411712	2026-01-06 22:18:40.411712	0
88	90	2026-01-06 22:20:05.812797	2026-01-06 22:20:05.812797	0
89	18	2026-01-07 21:16:13.139311	2026-01-07 21:16:13.139311	0
90	92	2026-01-07 21:27:13.576031	2026-01-07 21:27:13.576031	0
91	93	2026-01-07 21:34:18.314555	2026-01-07 21:34:18.314555	0
92	94	2026-01-07 21:37:35.531934	2026-01-07 21:37:35.531934	0
93	95	2026-01-07 21:47:17.328228	2026-01-07 21:47:17.328228	0
94	54	2026-01-07 21:49:46.073757	2026-01-07 21:49:46.073757	0
95	96	2026-01-07 21:55:43.11085	2026-01-07 21:55:43.110850	0
96	19	2026-01-08 21:35:23.283798	2026-01-08 21:35:23.283798	0
97	97	2026-01-08 21:38:46.212877	2026-01-08 21:38:46.212877	0
98	98	2026-01-08 21:45:03.571552	2026-01-08 21:45:03.571552	0
99	69	2026-01-09 21:43:24.274947	2026-01-09 21:43:24.274947	0
100	99	2026-01-09 21:47:38.862173	2026-01-09 21:47:38.862173	0
101	100	2026-01-09 21:50:27.360396	2026-01-09 21:50:27.360396	0
102	101	2026-01-10 16:36:39.730373	2026-01-10 16:36:39.730373	0
103	102	2026-01-10 16:39:01.309188	2026-01-10 16:39:01.309188	0
104	103	2026-01-10 16:46:21.970712	2026-01-10 16:46:21.970712	0
105	11	2026-01-12 21:30:15.019524	2026-01-12 21:30:15.019524	0
106	31	2026-01-12 21:31:22.40907	2026-01-12 21:31:22.409070	0
107	104	2026-01-12 21:39:20.482224	2026-01-12 21:39:20.482224	0
108	105	2026-01-13 21:42:35.475511	2026-01-13 21:42:35.475511	0
109	106	2026-01-13 21:46:05.854923	2026-01-13 21:46:05.854923	0
110	107	2026-01-13 21:48:42.641145	2026-01-13 21:48:42.641145	0
111	108	2026-01-13 21:51:57.188018	2026-01-13 21:51:57.188018	0
112	18	2026-01-14 21:20:27.45837	2026-01-14 21:20:27.458370	0
113	110	2026-01-14 21:27:21.934387	2026-01-14 21:27:21.934387	0
114	113	2026-01-15 21:50:41.148919	2026-01-15 21:50:41.148919	0
115	52	2026-01-15 22:04:38.020997	2026-01-15 22:04:38.020997	0
116	10	2026-01-15 22:05:36.688762	2026-01-15 22:05:36.688762	0
117	117	2026-01-17 16:16:58.306786	2026-01-17 16:16:58.306786	0
118	102	2026-01-17 16:17:55.214648	2026-01-17 16:17:55.214648	0
119	8	2026-01-19 21:43:17.43138	2026-01-19 21:43:17.431380	0
120	118	2026-01-19 21:45:24.163336	2026-01-19 21:45:24.163336	0
121	119	2026-01-19 21:47:46.163644	2026-01-19 21:47:46.163644	0
122	117	2026-01-20 21:33:49.823221	2026-01-20 21:33:49.823221	0
123	71	2026-01-20 21:36:03.164069	2026-01-20 21:36:03.164069	0
124	88	2026-01-20 21:37:28.392865	2026-01-20 21:37:28.392865	0
125	122	2026-01-20 21:44:09.371573	2026-01-20 21:44:09.371573	0
126	124	2026-01-21 21:31:19.335185	2026-01-21 21:31:19.335185	0
127	125	2026-01-21 21:36:00.253208	2026-01-21 21:36:00.253208	0
128	100	2026-01-21 21:37:03.658667	2026-01-21 21:37:03.658667	0
129	126	2026-01-21 21:39:29.310903	2026-01-21 21:39:29.310903	0
130	20	2026-01-22 21:41:49.135728	2026-01-22 21:41:49.135728	0
131	128	2026-01-22 21:45:40.775413	2026-01-22 21:45:40.775413	0
132	129	2026-01-22 21:47:56.239138	2026-01-22 21:47:56.239138	0
133	130	2026-01-22 21:52:10.168248	2026-01-22 21:52:10.168248	0
134	90	2026-01-23 21:42:01.642383	2026-01-23 21:42:01.642383	0
135	131	2026-01-23 21:45:26.322206	2026-01-23 21:45:26.322206	0
136	41	2026-01-23 21:46:18.620575	2026-01-23 21:46:18.620575	0
137	132	2026-01-23 21:49:32.808947	2026-01-23 21:49:32.808947	0
138	38	2026-01-23 21:54:06.666996	2026-01-23 21:54:06.666996	0
139	134	2026-01-23 21:56:11.151257	2026-01-23 21:56:11.151257	0
140	136	2026-01-26 21:19:05.209817	2026-01-26 21:19:05.209817	0
141	137	2026-01-26 21:21:24.472876	2026-01-26 21:21:24.472876	0
142	59	2026-01-26 21:22:49.808637	2026-01-26 21:22:49.808637	0
143	138	2026-01-26 21:25:10.096408	2026-01-26 21:25:10.096408	0
144	139	2026-01-26 21:28:51.015045	2026-01-26 21:28:51.015045	0
145	140	2026-01-26 21:31:54.749397	2026-01-26 21:31:54.749397	0
146	141	2026-01-26 21:44:22.908999	2026-01-26 21:44:22.908999	0
147	143	2026-01-27 21:25:21.312721	2026-01-27 21:25:21.312721	0
148	144	2026-01-27 21:30:32.417598	2026-01-27 21:30:32.417598	0
149	145	2026-01-28 21:44:58.207323	2026-01-28 21:44:58.207323	0
150	138	2026-01-28 21:48:02.572758	2026-01-28 21:48:02.572758	0
151	36	2026-01-29 21:55:24.11187	2026-01-29 21:55:24.111870	0
152	62	2026-02-20 16:26:32.560745	2026-02-20 16:26:32.560745	0
153	153	2026-02-20 18:10:57.075534	2026-02-20 18:10:57.075534	0
154	124	2026-02-24 19:16:10.158276	2026-02-24 19:16:10.158276	0
155	152	2026-02-24 19:43:27.45348	2026-02-24 19:43:27.453480	0
156	160	2026-02-25 18:05:29.616517	2026-02-25 18:05:29.616517	0
157	149	2026-02-27 19:59:52.739179	2026-02-27 19:59:52.739179	0
158	157	2026-02-27 20:00:45.891013	2026-02-27 20:00:45.891013	0
159	161	2026-02-27 20:04:39.76166	2026-02-27 20:04:39.761660	0
160	162	2026-02-27 20:07:17.684575	2026-02-27 20:07:17.684575	0
161	163	2026-02-27 20:09:05.70408	2026-02-27 20:09:05.704080	0
162	30	2026-02-27 20:09:54.84511	2026-02-27 20:09:54.845110	0
163	164	2026-02-27 20:13:22.075987	2026-02-27 20:13:22.075987	0
164	165	2026-02-27 20:15:39.656746	2026-02-27 20:15:39.656746	0
165	149	2026-02-27 20:18:55.563622	2026-02-27 20:18:55.563622	0
166	159	2026-02-27 20:19:56.231383	2026-02-27 20:19:56.231383	0
167	100	2026-02-27 20:20:49.30515	2026-02-27 20:20:49.305150	0
168	139	2026-02-27 20:21:21.893865	2026-02-27 20:21:21.893865	0
169	108	2026-02-27 20:22:02.408539	2026-02-27 20:22:02.408539	0
170	174	2026-03-02 14:21:08.229548	2026-03-02 14:21:08.229548	0
171	175	2026-03-02 14:21:39.677868	2026-03-02 14:21:39.677868	0
172	92	2026-03-02 14:26:06.705956	2026-03-02 14:26:06.705956	0
173	168	2026-03-02 14:27:03.570675	2026-03-02 14:27:03.570675	0
174	83	2026-03-02 14:29:21.031586	2026-03-02 14:29:21.031586	0
175	121	2026-03-02 14:30:01.340681	2026-03-02 14:30:01.340681	0
176	169	2026-03-02 14:30:37.527397	2026-03-02 14:30:37.527397	0
177	100	2026-03-02 14:32:00.878873	2026-03-02 14:32:00.878873	0
178	157	2026-03-02 14:34:36.236418	2026-03-02 14:34:36.236418	0
179	132	2026-03-02 14:35:19.793241	2026-03-02 14:35:19.793241	0
180	171	2026-03-02 14:36:13.643911	2026-03-02 14:36:13.643911	0
181	11	2026-03-02 14:42:48.024637	2026-03-02 14:42:48.024637	0
182	62	2026-03-02 14:43:47.242187	2026-03-02 14:43:47.242187	0
183	144	2026-03-02 14:45:18.77056	2026-03-02 14:45:18.770560	0
184	59	2026-03-02 14:52:33.07623	2026-03-02 14:52:33.076230	0
185	172	2026-03-02 14:54:51.885091	2026-03-02 14:54:51.885091	0
186	50	2026-03-02 14:55:50.29116	2026-03-02 14:55:50.291160	0
187	161	2026-03-02 14:56:29.536255	2026-03-02 14:56:29.536255	0
188	173	2026-03-02 15:00:59.550375	2026-03-02 15:00:59.550375	0
189	166	2026-03-02 15:01:37.756923	2026-03-02 15:01:37.756923	0
190	150	2026-03-02 15:04:58.928758	2026-03-02 15:04:58.928758	0
191	177	2026-03-02 15:06:20.945498	2026-03-02 15:06:20.945498	0
192	176	2026-03-02 15:07:38.29873	2026-03-02 15:07:38.298730	0
193	179	2026-03-02 15:11:09.226055	2026-03-02 15:11:09.226055	0
194	180	2026-03-02 15:12:52.290008	2026-03-02 15:12:52.290008	0
195	30	2026-03-02 15:18:39.427386	2026-03-02 15:18:39.427386	0
196	181	2026-03-02 17:06:37.17051	2026-03-02 17:06:37.170510	0
198	68	2026-03-02 21:18:18.601361	2026-03-02 21:18:18.601361	0
199	182	2026-03-02 21:24:57.024283	2026-03-02 21:24:57.024283	0
201	30	2026-03-02 21:25:36.522093	2026-03-02 21:25:36.522093	0
202	85	2026-03-02 21:26:27.557753	2026-03-02 21:26:27.557753	0
203	18	2026-03-02 21:29:20.168568	2026-03-02 21:29:20.168568	0
204	155	2026-03-02 21:30:30.186395	2026-03-02 21:30:30.186395	0
205	183	2026-03-04 18:16:13.795289	2026-03-04 18:16:13.795289	0
206	74	2026-03-04 18:17:17.369498	2026-03-04 18:17:17.369498	0
207	182	2026-03-04 18:18:35.765794	2026-03-04 18:18:35.765794	0
208	30	2026-03-04 18:19:04.024594	2026-03-04 18:19:04.024594	0
209	184	2026-03-04 18:20:32.009737	2026-03-04 18:20:32.009737	0
210	181	2026-03-04 18:21:12.044441	2026-03-04 18:21:12.044441	0
211	85	2026-03-04 18:23:03.726735	2026-03-04 18:23:03.726735	0
212	155	2026-03-04 18:26:04.734494	2026-03-04 18:26:04.734494	0
213	185	2026-03-04 20:08:44.296229	2026-03-04 20:08:44.296229	0
214	162	2026-03-11 18:21:30.840849	2026-03-11 18:21:30.840849	0
215	186	2026-03-11 18:24:23.174817	2026-03-11 18:24:23.174817	0
216	163	2026-03-11 18:27:33.205548	2026-03-11 18:27:33.205548	0
217	187	2026-03-11 18:29:30.471207	2026-03-11 18:29:30.471207	0
218	188	2026-03-11 18:30:55.652231	2026-03-11 18:30:55.652231	0
\.


--
-- Data for Name: tarea; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tarea (id, fecha_creacion, titulo, detalle, estado, prioridad, responsable, vencimiento) FROM stdin;
1	2026-03-19 23:58:53.390985	2026-01-12 20:28:47.771582	FORD RANGER FUGA	Pendiente	Media	\N	\N
2	2026-03-19 23:58:53.392363	2026-01-12 20:30:26.255517	MITSUBICHI L200 RTLD84	Pendiente	Media	\N	\N
5	2026-03-19 23:58:53.393433	2026-01-12 20:33:56.167632	MAXUS T60 PH	Pendiente	Media	\N	\N
6	2026-03-19 23:58:53.394461	2026-01-12 20:34:41.134994	PEUGEOT PARTNER	Pendiente	Media	\N	\N
7	2026-03-19 23:58:53.39551	2026-01-12 20:35:42.170821	CHERY TIGGO 7 BLANCO PH	Pendiente	Media	\N	\N
8	2026-03-19 23:58:53.396568	2026-01-12 20:38:11.186144	TOYOTA HILUX	Pendiente	Media	\N	\N
10	2026-03-19 23:58:53.397573	2026-01-12 20:40:20.999455	MAXUS T60 2.0 ROJA	Pendiente	Media	\N	\N
12	2026-03-19 23:58:53.398563	2026-01-12 20:42:19.678339	RENAULT DOKKER	Pendiente	Media	\N	\N
13	2026-03-19 23:58:53.399568	2026-01-12 21:13:13.130488	NISSAN TERRANO	Pendiente	Media	\N	\N
14	2026-03-19 23:58:53.400626	2026-01-12 21:14:21.048984	DSFK	Pendiente	Media	\N	\N
16	2026-03-19 23:58:53.401669	2026-01-12 21:20:03.867246	GAC ROJO	Pendiente	Media	\N	\N
18	2026-03-19 23:58:53.402695	2026-01-12 21:25:41.364526	KIA SELTOS	Pendiente	Media	\N	\N
19	2026-03-19 23:58:53.403735	2026-01-12 23:54:31.677173	suzuki grand nomade	Pendiente	Media	\N	\N
24	2026-03-19 23:58:53.404768	2026-01-17 15:12:18.690780	PEUGEOT 2008	Pendiente	Media	\N	\N
29	2026-03-19 23:58:53.405896	2026-01-24 14:15:45.356715	MITSUBICHI L200 RDJJ94	Pendiente	Media	\N	\N
30	2026-03-19 23:58:53.406911	2026-03-06 18:53:15.881152	Mg zs kzwl31	Pendiente	Media	\N	\N
\.


--
-- Data for Name: toma_hora; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.toma_hora (id, fecha_creacion, fecha, responsable, actividad, detalle, horas, estado, urgencia, rapidez) FROM stdin;
2	2026-01-19 23:05:04.675625	2026-01-20	MAURICIO	MG ZS	lavado	3	Hecho	Normal	Hoy
3	2026-01-21 17:43:35.126169	2026-01-22	CRISTOBAL	CHERY TIGGO 7 SDRB49	REVISAR CHECK Y PASTILLAS	2	Hecho	Normal	Hoy
4	2026-01-22 13:19:19.796062	2026-01-22	MAURICIO	KIA SPORTAGE	LAVADO CLIENTE	1.3	Hecho	Normal	Hoy
5	2026-01-26 17:57:52.206583	2026-01-26	CRISTOBAL	HYUNDAI I10	CARGA AC BIELETAS	10	Hecho	Normal	Hoy
6	2026-02-03 12:48:00.830926	2026-02-03	\N	Chevrolet tracker	Nicolás barría, cambio de pastillas y otros servicios	10	Hecho	Normal	Hoy
7	2026-02-04 15:54:01.110009	2026-02-10	CRISTOBAL	GAC GS4 PRDS55	CAMBIO DE ACEITE Y ACEITE DE CAJA	10	Pendiente	Normal	Hoy
\.


--
-- Data for Name: usuario; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuario (id, username, password_hash, rol) FROM stdin;
1	cristobal	scrypt:32768:8:1$kFpFZcEkNS4t7nLi$20302498a696458883eb1e0a0624a6a63e7d62cf1163f2483a2cd637046fb43c1bde17d27e9484f59082debb89236787a1922cf6072783db8bf60eda50d416a0	admin
2	mauriciolop88	scrypt:32768:8:1$zWBdXmTaB9XwjGfm$6d019ea7ab7564e8f0ce96f50f57616169c5803dfa91b1bcca2d2a63b7547ee81352f8e74014e1b0999436c5fc231406f792b19846d2175df58b83f2ea564661	visualizador
3	nulo	scrypt:32768:8:1$rqCCMpSd7qig6Ur9$7c50a8ed9c5c8ef34fd071441d544fac4b977541e5f2a5f0d55f267264d1c3db9079d02cbf0c91b1b59679b40be48bc2acde0b619b3a7e9e2fa91f876fdd83a1	visualizador
4	carlos	scrypt:32768:8:1$nasIRiXjEIcI77eD$9725212f6b43f010a11ac6c7b6824ea22d55aaf8687b030d7b7d8af86f05613015302c312f8227ed271fa8cfcbb89faef8741716bd417272543d3ad3aea1ce28	operador
5	FRANCISCO	scrypt:32768:8:1$tBZGzBG7T4q9lX0f$df0fc2690bcc27d344bc1f1d97ccdbb2b230f363c06fc09393703a5366b8d3773f271b7a05ad490b4dd68d79c9a3227b341ca42654ec03b56a85db6d01b41e6c	admin
6	NICOLM	scrypt:32768:8:1$c3qYUVnCUVv91o1u$86505ae84757cb0fd5d385e28009729d90613480fd57a3f3804fae12daac5f1a444ca48faea4e00819b263eb6823953bdf73a2e7fc30c98bd0ea752533d41f2e	lector
7	nicolpeña	scrypt:32768:8:1$lPHnKRrjy1NlAUcx$42bb230d9705298f83172113978725972cc6bf8bfd252d2c4d348e255a0d2a73056724a1e42127c98d579e74909ca2ec89facbc77323dd21a907f433e313dc15	admin
8	nicoledelapeña	scrypt:32768:8:1$Z4OlW4G71gaZYafZ$7d0c3f8b5901b6508365909c84abc063808150b72b992328b29f8ed8dca7cabcc9209203c8cf864400fd85b7277e0dd1fe1afde86294bf8bf65320ee48cbe236	lector
9	seba	scrypt:32768:8:1$4lg9jIOZKgroDZfK$082a81b764eedb4a9daa99c303bb7b8a2a7b755ae93f640df2ec63a089aa41ee42b72d5aba632b21f76357176db5e799259d0bf46955ad7560db38834906e211	visualizador
10	admin	scrypt:32768:8:1$jzfU6qlBj8QNsQhL$a76be7b3291b67a9f211a25d91444a207424ff5cbad11b1b3a8ee3bbfc17507ba1119496bb32a8a884dab572b4a42fdc2ac788ede3f0aa32eb4e659211d63e52	admin
\.


--
-- Data for Name: vehiculo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vehiculo (id, patente, modelo, cliente_id, foto, foto_mime) FROM stdin;
3	JXXR98	PEUGEOT 3008	9	\N	\N
4	LDZP19	Peugeot 3008 1.5 bluehdi	8	\N	\N
5	PJRP24	HILUX SRV	8	\N	\N
6	GSSZ78	MAHINDRA XUV500	8	\N	\N
7	PLYC57	JETOUR DASHING	11	\N	\N
8	SPRL94	GAC	8	\N	\N
9	RRBL15	KIA SPORTAGE	8	\N	\N
10	LGFW18	CHEVROLET SILVERADO	8	\N	\N
11	KCJC67	FORD F150	8	\N	\N
12	PKWG18	Mitsubishi L200	13	\N	\N
13	INFORMES	MENSUALES	8	\N	\N
14	RHCX14	HYUNDAI I20	12	\N	\N
15	PKRV23	SAVEIRO	8	\N	\N
16	CGLD21	TOYOTA 4 RUNNER	8	\N	\N
17	SPXD37	NISSAN XTRAIL	12	\N	\N
18	SXWZ90	HYUNDAI CRETA	8	\N	\N
19	RHCX64	MAXUS EV30	8	\N	\N
20	THVR15	FOTON	8	\N	\N
21	TLSY27	CHEVROLET CAPTIVA	12	\N	\N
22	KXXH86	CHEVROLET DIMAX	8	\N	\N
23	PZTT62	MAXUS EV30	8	\N	\N
24	HYZZ19	FORD EXPLORER	14	\N	\N
25	PGWS86	MAHINDRA PICK UP	15	\N	\N
26	SHHD20	JMC VIGUS PLUS	8	\N	\N
27	KXCK41	AUDI A3	12	\N	\N
28	FWTV26	NISSAN JUKE	12	\N	\N
29	LYYZ33	Mazda BT-50	16	\N	\N
30	PJRC50	PEUGEOT 2008	8	\N	\N
31	PPSR95	PEUGEOT PARTNER	8	\N	\N
33	RHPH66	VOLKSWAGEN TAOS TSI	12	\N	\N
34	FHVW31	Volvo xc60	17	\N	\N
35	KCKX46	TOYOTA HILUX	12	\N	\N
36	RKWD64	MAXUS T60	12	\N	\N
38	JDLR93	HYUNDAI ACCENT	8	\N	\N
39	FHCK43	CHEVROLET SAIL	8	\N	\N
40	JYLW19	NISSAN NP300	12	\N	\N
41	HFRT75	SUZUKI NOMADE	8	\N	\N
42	LHGP55	CHEVROLET DIMAX	12	\N	\N
43	RRTP81	JAC TB PRO	12	\N	\N
44	TPCG43	PEUGEOT TRAVELLER	12	\N	\N
45	PGFJ59	CHERY TIGGO 3	12	\N	\N
46	RWWV77	MAXUS V80	12	\N	\N
47	PKLF11	FORD ECO SPORT	12	\N	\N
48	LHHK42	BMW 320I	12	\N	\N
49	JZKF36	MITSUBISHI L200	8	\N	\N
50	JPDW84	SUZUKI SWIFT	18	\N	\N
51	LTLD41	FORD EDGE	12	\N	\N
52	RTYZ21	RENAULT DOKKER	12	\N	\N
53	JLKJ31	SUZUKI JIMNY	12	\N	\N
54	SBJB16	CHEVROLET TRAKKER	12	\N	\N
55	KLXP67	NISSAN XTRAIL	12	\N	\N
56	PJFR78	CHERY TIGGO 8	12	\N	\N
57	HTJY97	BMW X1	12	\N	\N
58	LCXG80	FORD F150 PLATINUM	12	\N	\N
59	PYFL19	GAC GS3	8	\N	\N
60	KJCW74	CHEVROLET SPIN	12	\N	\N
61	RJDG48	PEUGEOT PARTNER	12	\N	\N
62	RVLW36	FORD EDGE	19	\N	\N
63	PZTB52	MITSUBISHI MONTERO	9	\N	\N
64	GRYX39	CHEVROLET SONIC	18	\N	\N
65	SGRP15	PEUGEOT LANDTREK	8	\N	\N
66	PCRL63	TOYOTA HILUX SR	8	\N	\N
67	KHPY16	VOLKSWAGEN SAVEIRO	8	\N	\N
68	KZWL31	MG ZS	8	\N	\N
69	PCLH39	TOYOTA HILUX SR	12	\N	\N
70	FCJP59	FORD EXPLORER	8	\N	\N
71	RXTG44	TOYOTA RAV4	12	\N	\N
72	SLKJ15	MAXUS T60	8	\N	\N
73	RHDC65	MAXUS EV30	8	\N	\N
74	GZGT30	NISSAN SENTRA	8	\N	\N
75	JGRR16	PEUGEOT EXPERT	12	\N	\N
76	RVSY40	MITSUBISHI L200	12	\N	\N
77	RJWR74	CHERY TIGGO 7 PRO	8	\N	\N
78	GSZF57	NISSAN NAVARA	8	\N	\N
79	JBKD21	SUBARU XV	12	\N	\N
80	RVPH80	MG ZS	8	\N	\N
81	JVVF51	TOYOTA YARIS	20	\N	\N
82	55555	Fgggggg	22	\N	\N
83	RPRD87	Maxus t60	12	\N	\N
84	SGZL93	KIA SELTOS	8	\N	\N
85	KXYG73	FIAT 500X	12	\N	\N
86	TCLG60	CHERY TIGGO 2	12	\N	\N
87	LJJG64	RENAULT CLIO	12	\N	\N
88	JGGF71	TOYOTA HILUX	8	\N	\N
89	HTWP18	FORD RANGER	8	\N	\N
90	JJFP86	PEUGEOT EXPERT	12	\N	\N
91	PPDR38	CHERY TIGGO 8	23	\N	\N
92	FGGP95	Hyundai veloster	12	\N	\N
93	SVXV58	Subaru crosstrek	12	\N	\N
94	JRYT45	Ford explorer	12	\N	\N
95	DWJL98	Chevrolet otra xl	24	\N	\N
96	RCXT11	Chevrolet sail	12	\N	\N
97	LZDL25	Ford f150 platinum	8	\N	\N
98	PCWH60	Chevrolet np400	8	\N	\N
99	JCKJ31	Suzuki jimmy	12	\N	\N
100	SGZJ93	Kia seltos	8	\N	\N
101	SGVS15	Chery tiggo 2	12	\N	\N
102	KXDX56	Chevrolet trailglazer	12	\N	\N
103	KRHY39	Chery arrizo	12	\N	\N
104	PYRP48	Ford Explorer	25	\N	\N
105	GZJL35	Peugeot partner	8	\N	\N
106	RGDB58	Volkswagen polo	12	\N	\N
107	Hyundai	PGLJ87	12	\N	\N
108	JYDS41	Suzuki grand nomade	12	\N	\N
109	KLXS67	Nissan x-trail	12	\N	\N
110	KLXD67		12	\N	\N
111	SGKB25	TOYOTA HILUX	16	\N	\N
112	PKLG27	MITSUBISHI L200	12	\N	\N
113	DTZH33	KIA RIO 5	26	\N	\N
114	Ye4233	Ford Ecosport	27	\N	\N
115	RTYZ21	Renaut	8	\N	\N
116	LSGH73	SUZUKI BALENO	28	\N	\N
117	GYLL95	Hyundai grand i10	8	\N	\N
118	LWRF23	Ford f150	12	\N	\N
119	LYZD61	Chevrolet prisma	12	\N	\N
120	PKRV23	SAVEIRO	29	\N	\N
121	RDJJ94	MITSUBISHI L200	8	\N	\N
122	LRCZ21	Ford ecosport	12	\N	\N
123	PYFL19	GAC GS3	8	\N	\N
124	TFWJ10	Chery tiggo 7pro	12	\N	\N
125	TJLS14	MG zs	30	\N	\N
126	STPX64	Jac t8pro	12	\N	\N
127	SDRB49	CHERY TIGGO 7	31	\N	\N
128	SDJS56	Peugeot landtrek	8	\N	\N
129	KKYK36	Mazda cx-5	12	\N	\N
130	VHFH22	Kia sportage	32	\N	\N
131	FTBB50	Toyota corolla	33	\N	\N
132	PBFT60	Suzuki ertiga	8	\N	\N
133	Hyundai	Qashqay	8	\N	\N
134	LWGP33	Nissan qashqay	12	\N	\N
135	LPKW76	Toyota hilux	8	\N	\N
136	PLKW76	Toyota hilux	8	\N	\N
137	TCPJ25	Chevrolet onix	8	\N	\N
138	JWBT96	Ford f -150 platinum	12	\N	\N
139	SJKG29	Maxus t60	12	\N	\N
140	STSW37	Opel grabdland	34	\N	\N
141	RSHL64	Renault dokker	8	\N	\N
142	RSHL64	Renault dokker	8	\N	\N
143	XB4019	Nissan terrano	35	\N	\N
144	SCJY16	Hiunday tucson	37	\N	\N
145	Tlpl32	Kia soluto	12	\N	\N
146	PCJR57	volkswagen amarok	38	\N	\N
147	LCWY15	CHEVROLET TRACKER	41	\N	\N
148	GZJL35	PEUGEOT PARTNER	42	\N	\N
149	RXGF94	GW POER	8	\N	\N
150	RZVR33	MAXUS T60	8	\N	\N
152	SKXY38	CITROEN PARTNER MAXI	12	\N	\N
153	HSRS31	PEUGEOT 208	25	\N	\N
154	HTRL87	TOYOTA RAV4	12	\N	\N
155	SCZT68	DSFK 500	8	\N	\N
156	PCXF76	MAXUS T60	8	\N	\N
157	KJBY56	TOYOTA HILUX	8	\N	\N
158	TCRP31	CITROEN C3	8	\N	\N
159	RXGF97	GW POER	8	\N	\N
160	SFGF34	PEUGEOT 208	43	\N	\N
161	FSYG58	Kia sorento	12	\N	\N
162	LPFY56	F150	8	\N	\N
163	RVSS38	MITSUBISHI L200	8	\N	\N
164	YTLR87	TOYOTA RAV4	12	\N	\N
165	SKLH83	MAXXUS T60 blanca	8	\N	\N
166	RWKH11	MG3	44	\N	\N
167	RDLL71	RENAULT DOKKER	8	\N	\N
168	RCCC19	Hyundai verna	12	\N	\N
169	FRBX47	Hyundai Accent	12	\N	\N
170	RVSS38	MITSUBISHI L200	8	\N	\N
171	PCKV66	SUZUKI XL7	8	\N	\N
172	RYSX73	MG ZX	8	\N	\N
173	GGKY73	LATITUDE	12	\N	\N
174	RPBD80	NISSAN NAVARA	8	\N	\N
175	JCFF80	Kia sorento	8	\N	\N
176	SKYX38	Citroen multispace	8	\N	\N
177	LHKJ67	MAXXUS T60	8	\N	\N
178	HSRF95	TAHOE	45	\N	\N
179	HSRF95	TAHOE	45	\N	\N
180	KLGH53	FORD RANGER	12	\N	\N
181	JXWW75	BMW X7	12	\N	\N
182	RRYV92	CHEVROLET TRAKKER	12	\N	\N
183	VLKW71	MITSUBISHI OUTLANDER	46	\N	\N
184	SCWZ90	HYUNDAI CRETA	8	\N	\N
185	VKLF94	KIA SOLUTO	47	\N	\N
186	SKLH93	MAXXUS T60 PLOMA	8	\N	\N
187	GVKV61	MINI COOPER	48	\N	\N
188	JVVC68	TOYOTA HILUX	12	\N	\N
189	LLZR43	MAZDA BT50	49	\N	\N
190	FZGY73	Chevrolet sail	50	\N	\N
191	RKSR82	CHEVROLET COLORADO	51	\N	\N
\.


--
-- Name: cliente_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cliente_id_seq', 1, false);


--
-- Name: cotizacion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cotizacion_id_seq', 1, false);


--
-- Name: gasto_st_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.gasto_st_id_seq', 1, false);


--
-- Name: ot_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ot_id_seq', 1, false);


--
-- Name: repuesto_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.repuesto_id_seq', 39, true);


--
-- Name: repuesto_usado_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.repuesto_usado_id_seq', 1, false);


--
-- Name: servicio_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.servicio_id_seq', 1, false);


--
-- Name: tarea_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tarea_id_seq', 1, false);


--
-- Name: toma_hora_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.toma_hora_id_seq', 1, false);


--
-- Name: usuario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuario_id_seq', 10, true);


--
-- Name: vehiculo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.vehiculo_id_seq', 1, false);


--
-- Name: cliente cliente_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_pkey PRIMARY KEY (id);


--
-- Name: cotizacion cotizacion_numero_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cotizacion
    ADD CONSTRAINT cotizacion_numero_key UNIQUE (numero);


--
-- Name: cotizacion cotizacion_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cotizacion
    ADD CONSTRAINT cotizacion_pkey PRIMARY KEY (id);


--
-- Name: gasto_st gasto_st_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gasto_st
    ADD CONSTRAINT gasto_st_pkey PRIMARY KEY (id);


--
-- Name: ot ot_numero_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ot
    ADD CONSTRAINT ot_numero_key UNIQUE (numero);


--
-- Name: ot ot_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ot
    ADD CONSTRAINT ot_pkey PRIMARY KEY (id);


--
-- Name: repuesto repuesto_codigo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repuesto
    ADD CONSTRAINT repuesto_codigo_key UNIQUE (codigo);


--
-- Name: repuesto repuesto_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repuesto
    ADD CONSTRAINT repuesto_pkey PRIMARY KEY (id);


--
-- Name: repuesto_usado repuesto_usado_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repuesto_usado
    ADD CONSTRAINT repuesto_usado_pkey PRIMARY KEY (id);


--
-- Name: servicio servicio_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.servicio
    ADD CONSTRAINT servicio_pkey PRIMARY KEY (id);


--
-- Name: tarea tarea_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tarea
    ADD CONSTRAINT tarea_pkey PRIMARY KEY (id);


--
-- Name: toma_hora toma_hora_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.toma_hora
    ADD CONSTRAINT toma_hora_pkey PRIMARY KEY (id);


--
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id);


--
-- Name: usuario usuario_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_username_key UNIQUE (username);


--
-- Name: vehiculo vehiculo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehiculo
    ADD CONSTRAINT vehiculo_pkey PRIMARY KEY (id);


--
-- Name: ot ot_vehiculo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ot
    ADD CONSTRAINT ot_vehiculo_id_fkey FOREIGN KEY (vehiculo_id) REFERENCES public.vehiculo(id);


--
-- Name: repuesto_usado repuesto_usado_ot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repuesto_usado
    ADD CONSTRAINT repuesto_usado_ot_id_fkey FOREIGN KEY (ot_id) REFERENCES public.ot(id);


--
-- Name: repuesto_usado repuesto_usado_repuesto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repuesto_usado
    ADD CONSTRAINT repuesto_usado_repuesto_id_fkey FOREIGN KEY (repuesto_id) REFERENCES public.repuesto(id);


--
-- Name: servicio servicio_vehiculo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.servicio
    ADD CONSTRAINT servicio_vehiculo_id_fkey FOREIGN KEY (vehiculo_id) REFERENCES public.vehiculo(id);


--
-- Name: vehiculo vehiculo_cliente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehiculo
    ADD CONSTRAINT vehiculo_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.cliente(id);


--
-- PostgreSQL database dump complete
--

