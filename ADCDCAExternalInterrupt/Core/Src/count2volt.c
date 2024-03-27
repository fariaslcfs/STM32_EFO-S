#include <math.h>
#include <stdint.h>

#define Vref 3.3 // Reference voltage (in volts)

int max_count;

double count2volt(int res, int count){

	    max_count = pow(2, res) - 1;

	    return(Vref / max_count * count);
}
