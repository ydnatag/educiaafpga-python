#include <stdint.h>

struct uart {
	volatile uint32_t divisor;
	volatile uint32_t rx_data;
	volatile uint32_t rx_rdy;
	volatile uint32_t rx_err;
	volatile uint32_t tx_data;
	volatile uint32_t tx_rdy;
	volatile uint32_t zero0; // reserved
	volatile uint32_t zero1; // reserved
	volatile uint32_t ev_status;
	volatile uint32_t ev_pending;
	volatile uint32_t ev_enable;
};


void uart_putc(volatile struct uart * uart, char c) {
    while (uart->tx_rdy == 0);
    uart->tx_data = c;
}

void uart_puts(volatile struct uart * uart, char *str) {
    while (*str) {
        uart_putc(uart, *str);
        str++;
    }
}

void isr(void) {
}

int main(void) {
    volatile int i;
    volatile struct uart * UART0 = (struct uart *) 0x2000;
	while(1) {
        for(i=0; i<100000; i++);
        uart_puts(UART0, "Hello, world!\r\n");
    }
}
