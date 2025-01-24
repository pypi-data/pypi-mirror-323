use nalgebra::{Vector3, Vector4, VectorView, U1, U3, U4};

use crate::Float;

/// An object which behaves as a four-vector.
pub trait FourVector {
    /// The magnitude of the vector (with $`---+`$ signature).
    fn mag(&self) -> Float;
    /// The squared magnitude of the vector (with $`---+`$ signature).
    fn mag2(&self) -> Float;
    /// Yields the three-vector part.
    fn vec3(&self) -> VectorView<Float, U3, U1, U4>;
    /// Gives the vector boosted along a $`\vec{\beta}`$ vector.
    fn boost(&self, beta: &Vector3<Float>) -> Self;
}

/// An object which behaves as a four-momentum.
pub trait FourMomentum: FourVector {
    /// Energy
    fn e(&self) -> Float;
    /// Momentum in the $`x`$-direction
    fn px(&self) -> Float;
    /// Momentum in the $`y`$-direction
    fn py(&self) -> Float;
    /// Momentum in the $`z`$-direction
    fn pz(&self) -> Float;
    /// The three-momentum
    fn momentum(&self) -> VectorView<Float, U3, U1, U4>;
    /// The $`\gamma`$ factor $`\frac{1}{\sqrt{1 - \beta^2}}`$.
    fn gamma(&self) -> Float;
    /// The $`\vec{\beta}`$ vector $`\frac{\vec{p}}{E}`$.
    fn beta(&self) -> Vector3<Float>;
    /// The mass of the corresponding object.
    fn m(&self) -> Float;
    /// The squared mass of the corresponding object.
    fn m2(&self) -> Float;
    /// Pretty-prints the four-momentum.
    fn to_p4_string(&self) -> String {
        format!(
            "[e = {:.5}; p = ({:.5}, {:.5}, {:.5}); m = {:.5}]",
            self.e(),
            self.px(),
            self.py(),
            self.pz(),
            self.m()
        )
    }
}

/// Useful methods for three-dimensional vectors.
pub trait ThreeVector {
    /// The magnitude of the vector.
    fn mag(&self) -> Float;
    /// The squared magnitude of the vector.
    fn mag2(&self) -> Float;
    /// The cosine of the polar angle $`\theta`$.
    fn costheta(&self) -> Float;
    /// The polar angle $`\theta`$.
    fn theta(&self) -> Float;
    /// The azimuthal angle $`\phi`$.
    fn phi(&self) -> Float;
    /// Creates a unit vector in the direction of the input vector.
    fn unit(&self) -> Vector3<Float>;
}

/// Additional methods for treating a [`ThreeVector`] as a three-momentum.
pub trait ThreeMomentum: ThreeVector {
    /// Momentum in the $`x`$-direction
    fn px(&self) -> Float;
    /// Momentum in the $`y`$-direction
    fn py(&self) -> Float;
    /// Momentum in the $`z`$-direction
    fn pz(&self) -> Float;
    /// Converts this three-momentum to a four-momentum with the given mass.
    fn with_mass(&self, mass: Float) -> Vector4<Float>;
    /// Converts this three-momentum to a four-momentum with the given energy.
    fn with_energy(&self, energy: Float) -> Vector4<Float>;
}

impl FourVector for Vector4<Float> {
    fn mag(&self) -> Float {
        Float::sqrt(self.mag2())
    }

    fn mag2(&self) -> Float {
        self[3] * self[3] - (self[0] * self[0] + self[1] * self[1] + self[2] * self[2])
    }

    fn boost(&self, beta: &Vector3<Float>) -> Self {
        let b2 = beta.dot(beta);
        let gamma = 1.0 / Float::sqrt(1.0 - b2);
        let p3 =
            self.vec3() + beta * ((gamma - 1.0) * self.vec3().dot(beta) / b2 + gamma * self[3]);
        Vector4::new(p3.x, p3.y, p3.z, gamma * (self[3] + beta.dot(&self.vec3())))
    }

    fn vec3(&self) -> VectorView<Float, U3, U1, U4> {
        self.fixed_rows::<3>(0)
    }
}

impl FourMomentum for Vector4<Float> {
    fn px(&self) -> Float {
        self[0]
    }

    fn py(&self) -> Float {
        self[1]
    }

    fn pz(&self) -> Float {
        self[2]
    }

    fn e(&self) -> Float {
        self[3]
    }

    fn momentum(&self) -> VectorView<Float, U3, U1, U4> {
        self.vec3()
    }

    fn gamma(&self) -> Float {
        let beta = self.beta();
        let b2 = beta.dot(&beta);
        1.0 / Float::sqrt(1.0 - b2)
    }

    fn beta(&self) -> Vector3<Float> {
        self.momentum().unscale(self.e())
    }

    fn m(&self) -> Float {
        self.mag()
    }

    fn m2(&self) -> Float {
        self.mag2()
    }
}

impl ThreeMomentum for Vector3<Float> {
    fn px(&self) -> Float {
        self[0]
    }

    fn py(&self) -> Float {
        self[1]
    }

    fn pz(&self) -> Float {
        self[2]
    }

    fn with_mass(&self, mass: Float) -> Vector4<Float> {
        let e = Float::sqrt(mass.powi(2) + self.mag2());
        Vector4::new(self.px(), self.py(), self.pz(), e)
    }

    fn with_energy(&self, energy: Float) -> Vector4<Float> {
        Vector4::new(self.px(), self.py(), self.pz(), energy)
    }
}

impl ThreeVector for Vector3<Float> {
    fn mag(&self) -> Float {
        Float::sqrt(self.mag2())
    }

    fn mag2(&self) -> Float {
        self.dot(self)
    }

    fn costheta(&self) -> Float {
        self.z / self.mag()
    }

    fn theta(&self) -> Float {
        Float::acos(self.costheta())
    }

    fn phi(&self) -> Float {
        Float::atan2(self.y, self.x)
    }

    fn unit(&self) -> Vector3<Float> {
        self.unscale(self.mag())
    }
}

impl<'a> ThreeMomentum for VectorView<'a, Float, U3, U1, U4> {
    fn px(&self) -> Float {
        self[0]
    }

    fn py(&self) -> Float {
        self[1]
    }

    fn pz(&self) -> Float {
        self[2]
    }

    fn with_mass(&self, mass: Float) -> Vector4<Float> {
        let e = Float::sqrt(mass.powi(2) + self.mag2());
        Vector4::new(self.px(), self.py(), self.pz(), e)
    }

    fn with_energy(&self, energy: Float) -> Vector4<Float> {
        Vector4::new(self.px(), self.py(), self.pz(), energy)
    }
}

impl<'a> ThreeVector for VectorView<'a, Float, U3, U1, U4> {
    fn mag(&self) -> Float {
        Float::sqrt(self.mag2())
    }

    fn mag2(&self) -> Float {
        self.dot(self)
    }

    fn costheta(&self) -> Float {
        self.z / self.mag()
    }

    fn theta(&self) -> Float {
        Float::acos(self.costheta())
    }

    fn phi(&self) -> Float {
        Float::atan2(self.y, self.x)
    }

    fn unit(&self) -> Vector3<Float> {
        self.to_owned().unscale(self.mag())
    }
}

#[cfg(test)]
mod tests {
    use approx::assert_relative_eq;
    use nalgebra::vector;

    use super::*;

    #[test]
    fn test_three_to_four_momentum_conversion() {
        let p3 = vector![1.0, 2.0, 3.0];
        let target_p4 = vector![1.0, 2.0, 3.0, 10.0];
        let p4_from_mass = p3.with_mass(target_p4.m());
        assert_eq!(target_p4.e(), p4_from_mass.e());
        assert_eq!(target_p4.px(), p4_from_mass.px());
        assert_eq!(target_p4.py(), p4_from_mass.py());
        assert_eq!(target_p4.pz(), p4_from_mass.pz());
        let p4_from_energy = p3.with_energy(target_p4.e());
        assert_eq!(target_p4.e(), p4_from_energy.e());
        assert_eq!(target_p4.px(), p4_from_energy.px());
        assert_eq!(target_p4.py(), p4_from_energy.py());
        assert_eq!(target_p4.pz(), p4_from_energy.pz());
    }

    #[test]
    fn test_four_momentum_basics() {
        let p = vector![3.0, 4.0, 5.0, 10.0];
        assert_eq!(p.e(), 10.0);
        assert_eq!(p.px(), 3.0);
        assert_eq!(p.py(), 4.0);
        assert_eq!(p.pz(), 5.0);
        assert_eq!(p.momentum().px(), 3.0);
        assert_eq!(p.momentum().py(), 4.0);
        assert_eq!(p.momentum().pz(), 5.0);
        assert_relative_eq!(p.beta().x, 0.3);
        assert_relative_eq!(p.beta().y, 0.4);
        assert_relative_eq!(p.beta().z, 0.5);
        assert_relative_eq!(p.m2(), 50.0);
        assert_relative_eq!(p.m(), Float::sqrt(50.0));
        assert_eq!(
            format!("{}", p.to_p4_string()),
            "[e = 10.00000; p = (3.00000, 4.00000, 5.00000); m = 7.07107]"
        );
    }

    #[test]
    fn test_three_momentum_basics() {
        let p = vector![3.0, 4.0, 5.0, 10.0];
        let q = vector![1.2, -3.4, 7.6, 0.0];
        let p3_view = p.momentum();
        let q3_view = q.momentum();
        assert_eq!(p3_view.px(), 3.0);
        assert_eq!(p3_view.py(), 4.0);
        assert_eq!(p3_view.pz(), 5.0);
        assert_relative_eq!(p3_view.mag2(), 50.0);
        assert_relative_eq!(p3_view.mag(), Float::sqrt(50.0));
        assert_relative_eq!(p3_view.costheta(), 5.0 / Float::sqrt(50.0));
        assert_relative_eq!(p3_view.theta(), Float::acos(5.0 / Float::sqrt(50.0)));
        assert_relative_eq!(p3_view.phi(), Float::atan2(4.0, 3.0));
        assert_relative_eq!(
            p3_view.unit(),
            vector![3.0, 4.0, 5.0].unscale(Float::sqrt(50.0))
        );
        assert_relative_eq!(p3_view.cross(&q3_view), vector![47.4, -16.8, -15.0]);
        let p3 = vector![3.0, 4.0, 5.0];
        let q3 = vector![1.2, -3.4, 7.6];
        assert_eq!(p3.px(), 3.0);
        assert_eq!(p3.py(), 4.0);
        assert_eq!(p3.pz(), 5.0);
        assert_relative_eq!(p3.mag2(), 50.0);
        assert_relative_eq!(p3.mag(), Float::sqrt(50.0));
        assert_relative_eq!(p3.costheta(), 5.0 / Float::sqrt(50.0));
        assert_relative_eq!(p3.theta(), Float::acos(5.0 / Float::sqrt(50.0)));
        assert_relative_eq!(p3.phi(), Float::atan2(4.0, 3.0));
        assert_relative_eq!(p3.unit(), vector![3.0, 4.0, 5.0].unscale(Float::sqrt(50.0)));
        assert_relative_eq!(p3.cross(&q3), vector![47.4, -16.8, -15.0]);
    }

    #[test]
    fn test_boost_com() {
        let p = vector![3.0, 4.0, 5.0, 10.0];
        let zero = p.boost(&-p.beta());
        assert_relative_eq!(zero[0], 0.0);
        assert_relative_eq!(zero[1], 0.0);
        assert_relative_eq!(zero[2], 0.0);
    }

    #[test]
    fn test_boost() {
        let p1 = vector![3.0, 4.0, 5.0, 10.0];
        let p2 = vector![3.4, 2.3, 1.2, 9.0];
        let p1_boosted = p1.boost(&-p2.beta());
        assert_relative_eq!(
            p1_boosted.e(),
            8.157632144622882,
            epsilon = Float::EPSILON.sqrt()
        );
        assert_relative_eq!(
            p1_boosted.px(),
            -0.6489200627053444,
            epsilon = Float::EPSILON.sqrt()
        );
        assert_relative_eq!(
            p1_boosted.py(),
            1.5316128987581492,
            epsilon = Float::EPSILON.sqrt()
        );
        assert_relative_eq!(
            p1_boosted.pz(),
            3.712145860221643,
            epsilon = Float::EPSILON.sqrt()
        );
    }
}
