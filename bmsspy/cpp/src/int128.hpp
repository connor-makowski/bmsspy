#pragma once

#include <cstdint>
#include <cstddef>
#include <cmath>
#include <stdexcept>
#include <iostream>

#if defined(_MSC_VER)
#include <intrin.h>
#endif

namespace bmsspy {

#if defined(__SIZEOF_INT128__) && !defined(BMSSPY_FORCE_CUSTOM_INT128)
using dist_t = __int128_t;
constexpr dist_t INF_VAL = static_cast<__int128_t>((static_cast<unsigned __int128>(1) << 126) - 1);
#else

struct Int128 {
    int64_t hi;
    uint64_t lo;

    constexpr Int128() : hi(0), lo(0) {}
    constexpr Int128(int64_t h, uint64_t l) : hi(h), lo(l) {}
    constexpr Int128(int v) : hi(v < 0 ? -1 : 0), lo(static_cast<uint64_t>(static_cast<int64_t>(v))) {}
    constexpr Int128(unsigned int v) : hi(0), lo(v) {}
    constexpr Int128(long v) : hi(v < 0 ? -1 : 0), lo(static_cast<uint64_t>(static_cast<int64_t>(v))) {}
    constexpr Int128(unsigned long v) : hi(0), lo(v) {}
    constexpr Int128(long long v) : hi(v < 0 ? -1 : 0), lo(static_cast<uint64_t>(v)) {}
    constexpr Int128(unsigned long long v) : hi(0), lo(v) {}

    Int128(float f) : Int128(static_cast<double>(f)) {}

    Int128(double d) {
        if (d <= 0.0) {
            hi = 0;
            lo = 0;
        } else {
            constexpr double two64 = 18446744073709551616.0;
            double h = std::floor(d / two64);
            double l = d - h * two64;
            hi = static_cast<int64_t>(h);
            lo = static_cast<uint64_t>(l);
        }
    }

    Int128(long double d) {
        if (d <= 0.0L) {
            hi = 0;
            lo = 0;
        } else {
            constexpr long double two64 = 18446744073709551616.0L;
            long double h = std::floor(d / two64);
            long double l = d - h * two64;
            hi = static_cast<int64_t>(h);
            lo = static_cast<uint64_t>(l);
        }
    }

    explicit operator double() const {
        constexpr double two64 = 18446744073709551616.0;
        return static_cast<double>(hi) * two64 + static_cast<double>(lo);
    }

    explicit operator int64_t() const {
        return static_cast<int64_t>(lo);
    }

    explicit operator bool() const {
        return hi != 0 || lo != 0;
    }

    friend constexpr Int128 operator+(const Int128& a, const Int128& b) {
        uint64_t lo = a.lo + b.lo;
        int64_t hi = a.hi + b.hi + (lo < a.lo ? 1 : 0);
        return Int128(hi, lo);
    }

    Int128& operator+=(const Int128& o) {
        *this = *this + o;
        return *this;
    }

    friend constexpr Int128 operator-(const Int128& a, const Int128& b) {
        uint64_t lo = a.lo - b.lo;
        int64_t hi = a.hi - b.hi - (a.lo < b.lo ? 1 : 0);
        return Int128(hi, lo);
    }

    Int128& operator-=(const Int128& o) {
        *this = *this - o;
        return *this;
    }

    static inline void mul64(uint64_t a, uint64_t b, uint64_t& hi, uint64_t& lo) {
#if defined(_MSC_VER) && defined(_M_X64)
        lo = _umul128(a, b, &hi);
#elif defined(_MSC_VER) && defined(_M_ARM64)
        lo = a * b;
        hi = __umulh(a, b);
#elif defined(__SIZEOF_INT128__)
        unsigned __int128 p = static_cast<unsigned __int128>(a) * b;
        lo = static_cast<uint64_t>(p);
        hi = static_cast<uint64_t>(p >> 64);
#else
        uint64_t a_lo = a & 0xFFFFFFFFULL, a_hi = a >> 32;
        uint64_t b_lo = b & 0xFFFFFFFFULL, b_hi = b >> 32;
        uint64_t p0 = a_lo * b_lo;
        uint64_t p1 = a_hi * b_lo;
        uint64_t p2 = a_lo * b_hi;
        uint64_t p3 = a_hi * b_hi;
        uint64_t cy = ((p0 >> 32) + (p1 & 0xFFFFFFFFULL) + (p2 & 0xFFFFFFFFULL)) >> 32;
        lo = p0 + (p1 << 32) + (p2 << 32);
        hi = p3 + (p1 >> 32) + (p2 >> 32) + cy;
#endif
    }

    friend inline Int128 operator*(const Int128& a, const Int128& b) {
        uint64_t hi, lo;
        mul64(a.lo, b.lo, hi, lo);
        hi += static_cast<uint64_t>(a.hi) * b.lo + a.lo * static_cast<uint64_t>(b.hi);
        return Int128(static_cast<int64_t>(hi), lo);
    }

    Int128& operator*=(const Int128& o) {
        *this = *this * o;
        return *this;
    }

    friend inline Int128 operator/(const Int128& a, const Int128& b) {
        if (b.hi == 0 && b.lo == 0) throw std::domain_error("Division by zero");
        if (a < b) return Int128(0);
        if (a == b) return Int128(1);

        if (a.hi == 0 && b.hi == 0) {
            return Int128(0, a.lo / b.lo);
        }

        Int128 rem(0);
        Int128 quo(0);
        for (int i = 127; i >= 0; --i) {
            rem.hi = (rem.hi << 1) | static_cast<int64_t>((rem.lo >> 63) & 1);
            rem.lo = (rem.lo << 1);

            uint64_t bit = 0;
            if (i >= 64) {
                bit = (static_cast<uint64_t>(a.hi) >> (i - 64)) & 1;
            } else {
                bit = (a.lo >> i) & 1;
            }
            rem.lo |= bit;

            if (rem >= b) {
                rem -= b;
                if (i >= 64) {
                    quo.hi |= static_cast<int64_t>(1ULL << (i - 64));
                } else {
                    quo.lo |= (1ULL << i);
                }
            }
        }
        return quo;
    }

    Int128& operator/=(const Int128& o) {
        *this = *this / o;
        return *this;
    }

    friend constexpr bool operator==(const Int128& a, const Int128& b) {
        return a.hi == b.hi && a.lo == b.lo;
    }

    friend constexpr bool operator!=(const Int128& a, const Int128& b) {
        return !(a == b);
    }

    friend constexpr bool operator<(const Int128& a, const Int128& b) {
        if (a.hi != b.hi) return a.hi < b.hi;
        return a.lo < b.lo;
    }

    friend constexpr bool operator<=(const Int128& a, const Int128& b) {
        return !(b < a);
    }

    friend constexpr bool operator>(const Int128& a, const Int128& b) {
        return b < a;
    }

    friend constexpr bool operator>=(const Int128& a, const Int128& b) {
        return !(a < b);
    }

    friend std::ostream& operator<<(std::ostream& os, const Int128& val) {
        return os << static_cast<double>(val);
    }
};

using dist_t = Int128;
constexpr dist_t INF_VAL = Int128(0x3FFFFFFFFFFFFFFFULL, 0xFFFFFFFFFFFFFFFFULL);

#endif

} // namespace bmsspy
