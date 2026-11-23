from django.test import TestCase, Client
from django.urls import reverse

from .modelos_colas import (
    analizar_costos,
    calcular_mm1,
    calcular_mms,
    ColaInestableError,
)


TOL = 1e-3


class MotorMM1Tests(TestCase):
    """Droguería: lambda = 10, mu = 12."""

    def setUp(self):
        self.r = calcular_mm1(10, 12)

    def test_rho(self):
        self.assertAlmostEqual(self.r.rho, 0.8333, delta=TOL)

    def test_p0(self):
        self.assertAlmostEqual(self.r.p0, 0.1667, delta=TOL)

    def test_l(self):
        self.assertAlmostEqual(self.r.l, 5.0, delta=TOL)

    def test_lq(self):
        self.assertAlmostEqual(self.r.lq, 4.1667, delta=TOL)

    def test_w(self):
        self.assertAlmostEqual(self.r.w, 0.5, delta=TOL)

    def test_wq(self):
        self.assertAlmostEqual(self.r.wq, 0.4167, delta=TOL)

    def test_little_l(self):
        self.assertAlmostEqual(self.r.l, self.r.lam * self.r.w, delta=TOL)

    def test_little_lq(self):
        self.assertAlmostEqual(self.r.lq, self.r.lam * self.r.wq, delta=TOL)


class MotorMMsTests(TestCase):
    """Banco: lambda = 20, mu = 8, s = 3."""

    def setUp(self):
        self.r = calcular_mms(20, 8, 3)

    def test_rho(self):
        self.assertAlmostEqual(self.r.rho, 0.8333, delta=TOL)

    def test_p0(self):
        self.assertAlmostEqual(self.r.p0, 0.0449, delta=TOL)

    def test_lq(self):
        self.assertAlmostEqual(self.r.lq, 3.5112, delta=TOL)

    def test_l(self):
        self.assertAlmostEqual(self.r.l, 6.0112, delta=TOL)

    def test_wq_min(self):
        self.assertAlmostEqual(self.r.wq * 60, 10.53, delta=1e-2)

    def test_w_min(self):
        self.assertAlmostEqual(self.r.w * 60, 18.03, delta=1e-2)

    def test_pw(self):
        self.assertAlmostEqual(self.r.pw, 0.7022, delta=TOL)

    def test_little(self):
        self.assertAlmostEqual(self.r.l, self.r.lam * self.r.w, delta=TOL)
        self.assertAlmostEqual(self.r.lq, self.r.lam * self.r.wq, delta=TOL)


class EquivalenciaMM1MMsTests(TestCase):
    """Con s=1, M/M/s debe coincidir con M/M/1."""

    def test_mismos_indicadores(self):
        r1 = calcular_mm1(10, 12)
        rs = calcular_mms(10, 12, 1)
        self.assertAlmostEqual(r1.rho, rs.rho, delta=TOL)
        self.assertAlmostEqual(r1.p0, rs.p0, delta=TOL)
        self.assertAlmostEqual(r1.l, rs.l, delta=TOL)
        self.assertAlmostEqual(r1.lq, rs.lq, delta=TOL)
        self.assertAlmostEqual(r1.w, rs.w, delta=TOL)
        self.assertAlmostEqual(r1.wq, rs.wq, delta=TOL)


class DistribucionTests(TestCase):
    def test_suma_pn_mm1_se_aproxima_a_1(self):
        r = calcular_mm1(10, 12, n_max=80)
        self.assertAlmostEqual(sum(r.distribucion), 1.0, delta=1e-3)

    def test_suma_pn_mms_se_aproxima_a_1(self):
        r = calcular_mms(20, 8, 3, n_max=80)
        self.assertAlmostEqual(sum(r.distribucion), 1.0, delta=1e-3)


class EstabilidadTests(TestCase):
    def test_mm1_inestable_lanza(self):
        with self.assertRaises(ColaInestableError):
            calcular_mm1(12, 10)

    def test_mms_inestable_lanza(self):
        with self.assertRaises(ColaInestableError):
            calcular_mms(30, 8, 3)

    def test_rechaza_s_no_entero(self):
        with self.assertRaises(ValueError):
            calcular_mms(10, 12, 1.5)  # type: ignore[arg-type]


class CostosTests(TestCase):
    """Banco: lambda=20, mu=8, Cs=15000, Cw=20000, s=3..6, base=L."""

    def setUp(self):
        self.r = analizar_costos(lam=20, mu=8, cs=15000, cw=20000, s_max=6, base="L")

    def test_s_minimo_estable(self):
        self.assertEqual(self.r.s_minimo_estable, 3)

    def test_s_optimo_es_4(self):
        self.assertEqual(self.r.s_optimo, 4)

    def test_ct_optimo_cercano_a_120662(self):
        self.assertAlmostEqual(self.r.costo_total_optimo, 120662, delta=500)

    def test_fila_s3_ct(self):
        fila = next(f for f in self.r.filas if f.s == 3)
        self.assertAlmostEqual(fila.costo_total, 165225, delta=500)

    def test_fila_s4_valores(self):
        fila = next(f for f in self.r.filas if f.s == 4)
        self.assertAlmostEqual(fila.rho, 0.625, delta=TOL)
        self.assertAlmostEqual(fila.l, 3.0331, delta=1e-2)
        self.assertAlmostEqual(fila.wq * 60, 1.60, delta=5e-2)

    def test_rechaza_smax_menor_que_smin(self):
        with self.assertRaises(ValueError):
            analizar_costos(lam=20, mu=8, cs=15000, cw=20000, s_max=2)


class VistasTests(TestCase):
    def setUp(self):
        self.c = Client()

    def test_inicio_200(self):
        self.assertEqual(self.c.get(reverse("inicio")).status_code, 200)

    def test_mm1_get_200(self):
        self.assertEqual(self.c.get(reverse("mm1")).status_code, 200)

    def test_mms_get_200(self):
        self.assertEqual(self.c.get(reverse("mms")).status_code, 200)

    def test_costos_get_200(self):
        self.assertEqual(self.c.get(reverse("costos")).status_code, 200)

    def test_mm1_cargar_ejemplo(self):
        resp = self.c.get(reverse("mm1") + "?ejemplo=1")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "10")

    def test_mm1_post_valido(self):
        resp = self.c.post(reverse("mm1"), {"lam": "10", "mu": "12", "unidad": "h", "n_max": "10"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "0,8333")

    def test_mm1_post_inestable_muestra_error(self):
        resp = self.c.post(reverse("mm1"), {"lam": "12", "mu": "10", "unidad": "h", "n_max": "10"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "no es estable")

    def test_mm1_post_negativo_muestra_error(self):
        resp = self.c.post(reverse("mm1"), {"lam": "-1", "mu": "12", "unidad": "h", "n_max": "10"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "mayor")
